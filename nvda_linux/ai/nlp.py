#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de traitement du langage naturel pour NVDA-Linux
====================================================

Utilise des modèles d'IA pour :
- Résumer du texte
- Traduire du texte
- Répondre à des questions
- Générer des descriptions
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    AutoModelForQuestionAnswering,
    pipeline,
)
from . import config

logger = logging.getLogger(__name__)

# Cache pour les modèles et tokenizers
_models: Dict[str, Any] = {}
_tokenizers: Dict[str, Any] = {}

def initialize(models: Dict[str, str], device: str = "cpu"):
    """Initialise les modèles NLP"""
    try:
        for name, model_id in models.items():
            if name == "text_summarization":
                _models[name] = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(device)
                _tokenizers[name] = AutoTokenizer.from_pretrained(model_id)
            elif name == "translation":
                _models[name] = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(device)
                _tokenizers[name] = AutoTokenizer.from_pretrained(model_id)
            elif name == "question_answering":
                _models[name] = AutoModelForQuestionAnswering.from_pretrained(model_id).to(device)
                _tokenizers[name] = AutoTokenizer.from_pretrained(model_id)
        
        logger.info("Initialisation des modèles NLP terminée")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des modèles NLP: {str(e)}")
        return False

def cleanup():
    """Nettoie les ressources des modèles NLP"""
    try:
        _models.clear()
        _tokenizers.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Nettoyage des modèles NLP terminé")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des modèles NLP: {str(e)}")

def load_model(model_name: str) -> Optional[Any]:
    """Charge un modèle NLP"""
    return _models.get(model_name)

def summarize_text(model: Any, text: str, max_length: int = 150) -> Optional[str]:
    """Résume un texte"""
    try:
        tokenizer = _tokenizers["text_summarization"]
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                min_length=30,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
        
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        logger.error(f"Erreur lors du résumé du texte: {str(e)}")
        return None

def translate_text(model: Any, text: str, target_lang: str = "en") -> Optional[str]:
    """Traduit un texte"""
    try:
        tokenizer = _tokenizers["translation"]
        inputs = tokenizer(text, return_tensors="pt", truncation=True).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.lang_code_to_id[target_lang],
                max_length=512
            )
        
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translation
    except Exception as e:
        logger.error(f"Erreur lors de la traduction: {str(e)}")
        return None

def answer_question(model: Any, question: str, context: str) -> Optional[Dict[str, Any]]:
    """Répond à une question sur un contexte"""
    try:
        tokenizer = _tokenizers["question_answering"]
        inputs = tokenizer(
            question,
            context,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(model.device)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits)
        
        answer = tokenizer.decode(
            inputs["input_ids"][0][answer_start:answer_end + 1],
            skip_special_tokens=True
        )
        
        confidence = torch.max(outputs.start_logits).item()
        
        return {
            "answer": answer,
            "confidence": confidence,
            "start": answer_start.item(),
            "end": answer_end.item()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la réponse à la question: {str(e)}")
        return None

def process_text(text: str, task: str = "summarize", **kwargs) -> Optional[Union[str, Dict[str, Any]]]:
    """Traite du texte selon la tâche demandée"""
    try:
        if task == "summarize":
            model = _models.get("text_summarization")
            if model:
                return summarize_text(model, text, **kwargs)
        elif task == "translate":
            model = _models.get("translation")
            if model:
                return translate_text(model, text, **kwargs)
        elif task == "qa":
            model = _models.get("question_answering")
            if model and "context" in kwargs:
                return answer_question(model, text, kwargs["context"])
        else:
            raise ValueError(f"Tâche NLP inconnue: {task}")
        
        return None
    except Exception as e:
        logger.error(f"Erreur lors du traitement du texte: {str(e)}")
        return None

def get_text_summary(text: str, max_length: int = 150) -> str:
    """Génère un résumé lisible d'un texte"""
    try:
        summary = process_text(text, "summarize", max_length=max_length)
        if summary:
            return summary
        
        # Fallback : extrait les phrases importantes
        sentences = text.split(". ")
        if len(sentences) > 3:
            return ". ".join(sentences[:3]) + "."
        return text
    except Exception as e:
        logger.error(f"Erreur lors de la génération du résumé: {str(e)}")
        return text[:max_length] + "..."

def translate_to_language(text: str, target_lang: str = "en") -> str:
    """Traduit un texte vers la langue cible"""
    try:
        translation = process_text(text, "translate", target_lang=target_lang)
        if translation:
            return translation
        
        # Fallback : retourne le texte original
        return text
    except Exception as e:
        logger.error(f"Erreur lors de la traduction: {str(e)}")
        return text

def answer_question_about_text(question: str, context: str) -> str:
    """Répond à une question sur un texte"""
    try:
        result = process_text(question, "qa", context=context)
        if result and result["answer"]:
            return f"{result['answer']} (confiance: {result['confidence']:.0%})"
        
        # Fallback : recherche de mots-clés
        keywords = question.lower().split()
        for keyword in keywords:
            if keyword in context.lower():
                start = context.lower().find(keyword)
                end = min(start + 100, len(context))
                return context[start:end] + "..."
        
        return "Je ne peux pas répondre à cette question."
    except Exception as e:
        logger.error(f"Erreur lors de la réponse à la question: {str(e)}")
        return "Erreur lors de l'analyse de la question." 