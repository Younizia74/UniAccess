#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de réalité augmentée pour NVDA-Linux
=========================================

Utilise des modèles d'IA pour :
- Estimer la profondeur
- Détecter la pose
- Analyser l'environnement
- Guider la navigation
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import torch
import numpy as np
from PIL import Image
import cv2
from transformers import (
    AutoModelForDepthEstimation,
    AutoImageProcessor,
    DetrImageProcessor,
    DetrForObjectDetection,
)
from . import config

logger = logging.getLogger(__name__)

# Cache pour les modèles et processeurs
_models: Dict[str, Any] = {}
_processors: Dict[str, Any] = {}

def initialize(models: Dict[str, str], device: str = "cpu"):
    """Initialise les modèles de réalité augmentée"""
    try:
        for name, model_id in models.items():
            if name == "depth_estimation":
                _models[name] = AutoModelForDepthEstimation.from_pretrained(model_id).to(device)
                _processors[name] = AutoImageProcessor.from_pretrained(model_id)
            elif name == "pose_estimation":
                _models[name] = DetrForObjectDetection.from_pretrained(model_id).to(device)
                _processors[name] = DetrImageProcessor.from_pretrained(model_id)
        
        logger.info("Initialisation des modèles de réalité augmentée terminée")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des modèles AR: {str(e)}")
        return False

def cleanup():
    """Nettoie les ressources des modèles AR"""
    try:
        _models.clear()
        _processors.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Nettoyage des modèles AR terminé")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des modèles AR: {str(e)}")

def load_model(model_name: str) -> Optional[Any]:
    """Charge un modèle AR"""
    return _models.get(model_name)

def estimate_depth(model: Any, image_path: str) -> Optional[Dict[str, Any]]:
    """Estime la profondeur dans une image"""
    try:
        image = Image.open(image_path).convert("RGB")
        processor = _processors["depth_estimation"]
        inputs = processor(images=image, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predicted_depth = outputs.predicted_depth
        
        # Normalise la profondeur
        depth_map = predicted_depth.squeeze().cpu().numpy()
        depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
        
        # Analyse les zones de profondeur
        zones = {
            "near": np.mean(depth_map[depth_map < 0.3]),
            "medium": np.mean(depth_map[(depth_map >= 0.3) & (depth_map < 0.7)]),
            "far": np.mean(depth_map[depth_map >= 0.7])
        }
        
        return {
            "depth_map": depth_map,
            "zones": zones,
            "min_depth": float(depth_map.min()),
            "max_depth": float(depth_map.max()),
            "mean_depth": float(depth_map.mean())
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'estimation de la profondeur: {str(e)}")
        return None

def estimate_pose(model: Any, image_path: str) -> Optional[Dict[str, Any]]:
    """Estime la pose et détecte les objets dans une image"""
    try:
        image = Image.open(image_path).convert("RGB")
        processor = _processors["pose_estimation"]
        inputs = processor(images=image, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Convertit les résultats en format lisible
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.7
        )[0]
        
        objects = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            objects.append({
                "label": model.config.id2label[label.item()],
                "confidence": score.item(),
                "box": box.tolist(),
                "center": [(box[0] + box[2])/2, (box[1] + box[3])/2]
            })
        
        return {
            "objects": objects,
            "image_size": image.size,
            "num_objects": len(objects)
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'estimation de la pose: {str(e)}")
        return None

def analyze_environment(image_path: str) -> Dict[str, Any]:
    """Analyse complète de l'environnement"""
    try:
        results = {}
        
        # Estimation de la profondeur
        depth_model = _models.get("depth_estimation")
        if depth_model:
            results["depth"] = estimate_depth(depth_model, image_path)
        
        # Estimation de la pose
        pose_model = _models.get("pose_estimation")
        if pose_model:
            results["pose"] = estimate_pose(pose_model, image_path)
        
        return results
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de l'environnement: {str(e)}")
        return {}

def get_environment_description(image_path: str) -> str:
    """Génère une description naturelle de l'environnement"""
    try:
        results = analyze_environment(image_path)
        description = []
        
        # Description de la profondeur
        if "depth" in results and results["depth"]:
            depth = results["depth"]
            zones = depth["zones"]
            description.append(
                f"Environnement avec des zones à {zones['near']:.0%} de profondeur proche, "
                f"{zones['medium']:.0%} de profondeur moyenne, "
                f"et {zones['far']:.0%} de profondeur lointaine."
            )
        
        # Description des objets
        if "pose" in results and results["pose"]:
            pose = results["pose"]
            if pose["objects"]:
                objects = [f"{obj['label']} ({obj['confidence']:.0%})" for obj in pose["objects"]]
                description.append(f"Objets détectés: {', '.join(objects)}")
            
            # Ajoute des informations de position
            if pose["objects"]:
                center_x = pose["image_size"][0] / 2
                center_y = pose["image_size"][1] / 2
                
                for obj in pose["objects"]:
                    x, y = obj["center"]
                    position = []
                    if x < center_x - 100:
                        position.append("à gauche")
                    elif x > center_x + 100:
                        position.append("à droite")
                    if y < center_y - 100:
                        position.append("en haut")
                    elif y > center_y + 100:
                        position.append("en bas")
                    
                    if position:
                        description.append(
                            f"{obj['label']} est {', '.join(position)}"
                        )
        
        return " ".join(description) if description else "Impossible de décrire l'environnement"
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la description: {str(e)}")
        return "Erreur lors de l'analyse de l'environnement"

def get_navigation_guidance(image_path: str) -> str:
    """Génère des instructions de navigation basées sur l'analyse de l'environnement"""
    try:
        results = analyze_environment(image_path)
        guidance = []
        
        if "depth" in results and results["depth"]:
            depth = results["depth"]
            if depth["mean_depth"] < 0.3:
                guidance.append("Attention : obstacles proches détectés")
            elif depth["mean_depth"] > 0.7:
                guidance.append("Espace dégagé devant")
        
        if "pose" in results and results["pose"]:
            pose = results["pose"]
            if pose["objects"]:
                # Trie les objets par distance (basé sur la position Y)
                sorted_objects = sorted(
                    pose["objects"],
                    key=lambda x: x["center"][1]
                )
                
                # Prend les 3 objets les plus proches
                for obj in sorted_objects[:3]:
                    x, y = obj["center"]
                    center_x = pose["image_size"][0] / 2
                    
                    if x < center_x - 100:
                        guidance.append(f"{obj['label']} sur votre gauche")
                    elif x > center_x + 100:
                        guidance.append(f"{obj['label']} sur votre droite")
                    else:
                        guidance.append(f"{obj['label']} devant vous")
        
        return " ".join(guidance) if guidance else "Aucune instruction de navigation disponible"
    except Exception as e:
        logger.error(f"Erreur lors de la génération des instructions: {str(e)}")
        return "Erreur lors de l'analyse de la navigation" 