package org.nvda;

import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.util.Log;

public class AccessibilityServiceSkeleton extends AccessibilityService {
    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // Exemple : log l'événement
        Log.d("NVDA-Android", "Event: " + event.toString());
        // Ici, tu pourrais envoyer l'info à l'app Python via socket, fichier, etc.
    }

    @Override
    public void onInterrupt() {
        // Gestion des interruptions
    }
} 