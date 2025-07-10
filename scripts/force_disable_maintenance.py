#!/usr/bin/env python
"""
Script para forzar desactivación del modo mantenimiento
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import db, MaintenanceMode

def force_disable_maintenance():
    """Forzar desactivación del modo mantenimiento"""
    app = create_app()
    
    with app.app_context():
        m = MaintenanceMode.query.first()
        print(f"Maintenance found: {m}")
        
        if m:
            print(f"Is active: {m.is_active}")
            print(f"Message: {m.message}")
            print(f"Started by: {m.started_by}")
            print(f"Started at: {m.started_at}")
            
            # Force deactivate
            m.is_active = False
            m.started_by = None
            m.started_at = None
            m.estimated_end = None
            m.message = "Sistema en mantenimiento. Volveremos pronto."
            
            db.session.commit()
            print("✅ Force deactivated!")
        else:
            print("No maintenance record found, creating one...")
            m = MaintenanceMode(is_active=False)
            db.session.add(m)
            db.session.commit()
            print("✅ Created inactive maintenance record")

if __name__ == "__main__":
    force_disable_maintenance()
