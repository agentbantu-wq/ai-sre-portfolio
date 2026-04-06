#!/usr/bin/env python3
"""
GitLab Contributors Hackathon Interactive Tool
Access GitLab using authenticated browser session with cookies
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import glob
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

console = Console()

class GitLabHackathonInteractive:
    """Interactive GitLab hackathon participation tool"""
    
    def __init__(self):
        # Load environment from .env file
        load_dotenv()
        
        self.driver = None
        self.chrome_user_data_dir = os.getenv('CHROME_USER_DATA_DIR')
        self.console = console
        
    def setup_browser(self):
        """Setup browser with authenticated session"""
        if self.driver:
            return
            
        try:
            options = Options()
            
            # Use Chrome user profile with cookies
            if self.chrome_user_data_dir and os.path.exists(self.chrome_user_data_dir):
                options.add_argument(f'--user-data-dir={self.chrome_user_data_dir}')
                self.console.print(f"✅ Using authenticated Chrome profile: {self.chrome_user_data_dir}")
            else:
                self.console.print("❌ Chrome user data directory not found")
                sys.exit(1)
            
            # Anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Stability
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            
            # Get chromedriver
            service = Service(ChromeDriverManager().install())
            chromedriver_path = service.path
            
            # Fix webdriver-manager path issue
            if 'THIRD_PARTY_NOTICES' in chromedriver_path:
                chromedriver_dir = os.path.dirname(os.path.dirname(chromedriver_path))
                actual_drivers = glob.glob(os.path.join(chromedriver_dir, '**', 'chromedriver'), recursive=True)
                if actual_drivers:
                    chromedriver_path = actual_drivers[0]
                    service = Service(chromedriver_path)
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.console.print("✅ Browser initialized with authenticated session")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Failed to setup browser: {e}")
            return False
    
    def check_authentication(self):
        """Check if user is logged into GitLab"""
        try:
            self.driver.get('https://gitlab.com/dashboard')
            
            # Wait for page to load
            time.sleep(2)
            
            # Check if logged in by looking for dashboard elements
            if 'dashboard' in self.driver.current_url.lower():
                self.console.print("✅ Successfully logged into GitLab!")
                return True
            else:
                self.console.print("❌ Not authenticated to GitLab")
                return False
                
        except Exception as e:
            self.console.print(f"❌ Error checking authentication: {e}")
            return False
    
    def view_hackathon_page(self):
        """Open and display GitLab hackathon page"""
        try:
            self.console.print("\n📖 Opening GitLab Hackathon page...")
            self.driver.get('https://contributors.gitlab.com/hackathon')
            time.sleep(3)
            
            self.console.print("✅ Hackathon page loaded successfully!")
            self.console.print("   https://contributors.gitlab.com/hackathon")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error loading hackathon page: {e}")
            return False
    
    def view_profile(self):
        """View your GitLab contributor profile"""
        try:
            self.console.print("\n👤 Opening your contributor profile...")
            self.driver.get('https://contributors.gitlab.com/users/me')
            time.sleep(2)
            
            self.console.print("✅ Profile page loaded!")
            self.console.print("   https://contributors.gitlab.com/users/me")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error loading profile: {e}")
            return False
    
    def find_issues(self):
        """Navigate to find issues page"""
        try:
            self.console.print("\n🔍 Opening issue finder...")
            self.driver.get('https://contributors.gitlab.com/find-issues')
            time.sleep(2)
            
            self.console.print("✅ Issue finder loaded!")
            self.console.print("   https://contributors.gitlab.com/find-issues")
            self.console.print("   💡 Look for 'quick-win' issues - they're perfect for starting out")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error loading issue finder: {e}")
            return False
    
    def view_leaderboard(self):
        """View hackathon leaderboard"""
        try:
            self.console.print("\n🏆 Opening hackathon leaderboard...")
            self.driver.get('https://contributors.gitlab.com/leaderboard/hackathons')
            time.sleep(2)
            
            self.console.print("✅ Leaderboard loaded!")
            self.console.print("   https://contributors.gitlab.com/leaderboard/hackathons")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error loading leaderboard: {e}")
            return False
    
    def show_menu(self):
        """Display interactive menu"""
        while True:
            self.console.print("\n")
            self.console.print(Panel(
                "[bold cyan]GitLab Contributors Hackathon[/bold cyan]\n"
                "[yellow]April 16-23, 2026[/yellow]\n\n"
                "Using your authenticated browser session with cookies",
                title="🚀 Interactive Tool"
            ))
            
            table = Table(title="Menu Options")
            table.add_column("Option", style="cyan")
            table.add_column("Action", style="magenta")
            
            table.add_row("1", "View Hackathon Page")
            table.add_row("2", "Open Your Profile")
            table.add_row("3", "Find Issues to Work On")
            table.add_row("4", "View Leaderboard")
            table.add_row("5", "Check Authentication Status")
            table.add_row("6", "Open in Browser (keep running)")
            table.add_row("0", "Exit")
            
            self.console.print(table)
            
            try:
                choice = input("\n👉 Select option (0-6): ").strip()
                
                if choice == '1':
                    self.view_hackathon_page()
                elif choice == '2':
                    self.view_profile()
                elif choice == '3':
                    self.find_issues()
                elif choice == '4':
                    self.view_leaderboard()
                elif choice == '5':
                    self.check_authentication()
                elif choice == '6':
                    self.console.print("\n🌐 Browser will stay open. Close it manually when done.")
                    input("   Press Enter to keep browser open... (Ctrl+C to exit when ready)")
                    self.console.print("   Browser is still running. Use Ctrl+C to quit.")
                    time.sleep(1000)
                elif choice == '0':
                    self.console.print("\n👋 Goodbye! Good luck with the hackathon!")
                    break
                else:
                    self.console.print("❌ Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                self.console.print("\n\n👋 Exiting...")
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}")
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            self.console.print("✅ Browser closed")

def main():
    """Main entry point"""
    tool = GitLabHackathonInteractive()
    
    try:
        # Setup browser with authentication
        if not tool.setup_browser():
            sys.exit(1)
        
        # Verify authentication
        if not tool.check_authentication():
            console.print("\n⚠️  You may not be logged into GitLab.")
            console.print("   Please log in at https://gitlab.com/")
            console.print("   Alternatively, open the browser manually to complete login.")
        
        # Show interactive menu
        tool.show_menu()
        
    except Exception as e:
        console.print(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        tool.close()

if __name__ == '__main__':
    main()
