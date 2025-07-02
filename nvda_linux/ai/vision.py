#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de vision par ordinateur pour NVDA-Linux
=============================================

Utilise des modèles d'IA pour :
- Générer des descriptions d'images
- Détecter et identifier des objets
- Comprendre le contexte d'une scène
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import torch
import numpy as np
from PIL import Image
from transformers import (
    AutoModelForVision2Seq,
    AutoProcessor,
    DetrImageProcessor,
    DetrForObjectDetection,
    AutoModelForVision2Seq,
    AutoTokenizer,
)
import cv2

logger = logging.getLogger(__name__)

# Cache pour les modèles et processeurs
_models: Dict[str, Any] = {}
_processors: Dict[str, Any] = {}

def initialize(models: Dict[str, str], device: str = "cpu"):
    """Initialise les modèles de vision"""
    try:
        for name, model_id in models.items():
            if name == "image_captioning":
                _models[name] = AutoModelForVision2Seq.from_pretrained(model_id).to(device)
                _processors[name] = AutoProcessor.from_pretrained(model_id)
            elif name == "object_detection":
                _models[name] = DetrForObjectDetection.from_pretrained(model_id).to(device)
                _processors[name] = DetrImageProcessor.from_pretrained(model_id)
            elif name == "scene_understanding":
                _models[name] = AutoModelForVision2Seq.from_pretrained(model_id).to(device)
                _processors[name] = AutoTokenizer.from_pretrained(model_id)
        
        logger.info("Initialisation des modèles de vision terminée")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des modèles de vision: {str(e)}")
        return False

def cleanup():
    """Nettoie les ressources des modèles de vision"""
    try:
        _models.clear()
        _processors.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Nettoyage des modèles de vision terminé")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des modèles de vision: {str(e)}")

def load_model(model_name: str) -> Optional[Any]:
    """Charge un modèle de vision"""
    return _models.get(model_name)

def load_image(image_path: str) -> Optional[Image.Image]:
    """Charge et prétraite une image"""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image non trouvée: {image_path}")
        
        image = Image.open(image_path).convert("RGB")
        return image
    except Exception as e:
        logger.error(f"Erreur lors du chargement de l'image {image_path}: {str(e)}")
        return None

def generate_caption(model: Any, image_path: str) -> Optional[str]:
    """Génère une description d'image"""
    try:
        image = load_image(image_path)
        if image is None:
            return None
        
        processor = _processors["image_captioning"]
        inputs = processor(images=image, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=50)
        
        caption = processor.batch_decode(outputs, skip_special_tokens=True)[0]
        return caption
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la description: {str(e)}")
        return None

def detect_objects(model: Any, image_path: str) -> List[Dict[str, Any]]:
    """Détecte et identifie les objets dans une image"""
    try:
        image = load_image(image_path)
        if image is None:
            return []
        
        processor = _processors["object_detection"]
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
            })
        
        return objects
    except Exception as e:
        logger.error(f"Erreur lors de la détection d'objets: {str(e)}")
        return []

def understand_scene(model: Any, image_path: str) -> Optional[str]:
    """Analyse et comprend le contexte d'une scène"""
    try:
        image = load_image(image_path)
        if image is None:
            return None
        
        processor = _processors["scene_understanding"]
        inputs = processor(images=image, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=100)
        
        description = processor.batch_decode(outputs, skip_special_tokens=True)[0]
        return description
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la scène: {str(e)}")
        return None

def analyze_image(image_path: str) -> Dict[str, Any]:
    """Analyse complète d'une image avec tous les modèles"""
    try:
        results = {}
        
        # Description de l'image
        caption_model = _models.get("image_captioning")
        if caption_model:
            results["caption"] = generate_caption(caption_model, image_path)
        
        # Détection d'objets
        detection_model = _models.get("object_detection")
        if detection_model:
            results["objects"] = detect_objects(detection_model, image_path)
        
        # Compréhension de la scène
        scene_model = _models.get("scene_understanding")
        if scene_model:
            results["scene"] = understand_scene(scene_model, image_path)
        
        return results
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de l'image {image_path}: {str(e)}")
        return {}

def get_image_description(image_path: str) -> str:
    """Génère une description naturelle d'une image"""
    try:
        results = analyze_image(image_path)
        
        description = []
        
        # Ajoute la description principale
        if "caption" in results and results["caption"]:
            description.append(results["caption"])
        
        # Ajoute les objets détectés
        if "objects" in results and results["objects"]:
            objects = [f"{obj['label']} ({obj['confidence']:.0%})" for obj in results["objects"]]
            if objects:
                description.append(f"Objets détectés: {', '.join(objects)}")
        
        # Ajoute la compréhension de la scène
        if "scene" in results and results["scene"]:
            description.append(f"Contexte: {results['scene']}")
        
        return " ".join(description) if description else "Impossible de décrire l'image"
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la description: {str(e)}")
        return "Erreur lors de l'analyse de l'image" 