#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime

class ErrorLogger:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.log_dir = os.path.join(base_dir, 'logs')
        self.error_log_path = os.path.join(self.log_dir, 'error_log.txt')
        self.app_log_path = os.path.join(self.log_dir, 'fingerprint_privacy.log')
        
        # Log dizini yoksa oluştur
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # Hata günlüğü için logger yapılandırması
        self.error_logger = logging.getLogger('error_logger')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(self.error_log_path)
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Uygulama günlüğü için logger yapılandırması
        self.app_logger = logging.getLogger('app_logger')
        self.app_logger.setLevel(logging.INFO)
        
        app_handler = logging.FileHandler(self.app_log_path)
        app_handler.setLevel(logging.INFO)
        app_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        app_handler.setFormatter(app_formatter)
        self.app_logger.addHandler(app_handler)
        
    def log_error(self, error_title, error_details=None):
        """Hata mesajını günlüğe kaydet"""
        error_msg = f"{error_title}"
        if error_details:
            error_msg += f": {str(error_details)}"
            
        self.error_logger.error(error_msg)
        return error_msg
        
    def log_info(self, message):
        """Bilgi mesajını günlüğe kaydet"""
        self.app_logger.info(message)
        return message
        
    def get_recent_errors(self, count=10):
        """Son hataları getir"""
        errors = []
        if os.path.exists(self.error_log_path):
            with open(self.error_log_path, 'r') as f:
                lines = f.readlines()
                errors = lines[-count:] if len(lines) > count else lines
                
        return errors
        
    def get_recent_logs(self, count=50):
        """Son günlük kayıtlarını getir"""
        logs = []
        if os.path.exists(self.app_log_path):
            with open(self.app_log_path, 'r') as f:
                lines = f.readlines()
                logs = lines[-count:] if len(lines) > count else lines
                
        return logs