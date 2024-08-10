import requests
import json
import os
import time
import subprocess
from datetime import datetime
import psycopg2
from psycopg2 import sql

class ContainerVulnerabilityScanner:
    def __init__(self):
        self.WebAppURL = 'http://localhost:8000'
        self.ImageScannerTaskURL = self.WebAppURL + '/image_scanner_task/'
        self.db_connection = psycopg2.connect(
            dbname="your_database_name",
            user="your_username",
            password="your_password",
            host="localhost"
        )
        self.db_cursor = self.db_connection.cursor()

    def get_next_image(self):
        response = requests.get(self.ImageScannerTaskURL)
        if response.status_code == 200:
            return response.json()
        return None

    def download_image(self, image_name):
        try:
            subprocess.run(['docker', 'pull', image_name], check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to download image: {image_name}")
            return False

    def scan_image_with_grype(self, image_name):
        try:
            result = subprocess.run(['grype', image_name, '-o', 'json'], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Grype scan failed for image: {image_name}")
            print(f"Error: {e}")
            return None

    def parse_grype_results(self, grype_results, image_name):
        vulnerabilities = []
        for match in grype_results.get('matches', []):
            vulnerability = {
                'image_name': image_name,
                'vulnerability_id': match.get('vulnerability', {}).get('id'),
                'severity': match.get('vulnerability', {}).get('severity'),
                'package_name': match.get('artifact', {}).get('name'),
                'package_version': match.get('artifact', {}).get('version'),
                'fix_version': match.get('vulnerability', {}).get('fix', {}).get('versions', [None])[0],
                'scan_time': datetime.now().isoformat()
            }
            vulnerabilities.append(vulnerability)
        return vulnerabilities

    def store_vulnerabilities(self, vulnerabilities):
        insert_query = sql.SQL("""
            INSERT INTO vulnerabilities (
                image_name, vulnerability_id, severity, package_name, 
                package_version, fix_version, scan_time
            ) VALUES (
                %(image_name)s, %(vulnerability_id)s, %(severity)s, %(package_name)s, 
                %(package_version)s, %(fix_version)s, %(scan_time)s
            )
        """)
        
        try:
            self.db_cursor.executemany(insert_query, vulnerabilities)
            self.db_connection.commit()
        except Exception as e:
            print(f"Error storing vulnerabilities: {e}")
            self.db_connection.rollback()

    def remove_image(self, image_name):
        try:
            subprocess.run(['docker', 'rmi', image_name], check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to remove image: {image_name}")

    def scanner_task(self):
        while True:
            image_info = self.get_next_image()
            if not image_info:
                print("No more images to scan. Exiting.")
                break

            image_name = image_info['image_name']
            print(f"Processing image: {image_name}")

            if self.download_image(image_name):
                grype_results = self.scan_image_with_grype(image_name)
                if grype_results:
                    vulnerabilities = self.parse_grype_results(grype_results, image_name)
                    self.store_vulnerabilities(vulnerabilities)
                self.remove_image(image_name)
            
            time.sleep(1)  # Add a small delay to avoid overwhelming the system

    def __del__(self):
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_connection:
            self.db_connection.close()

if __name__ == '__main__':
    scanner = ContainerVulnerabilityScanner()
    scanner.scanner_task()