import sys
import pyautogui
from views.automation_view import AutomationView
from viewmodels.automation_viewmodel import AutomationViewModel

def setup_pyautogui():
    """PyAutoGUI ayarlarını yapılandırır"""
    pyautogui.MINIMUM_DURATION = 0.1
    pyautogui.MINIMUM_SLEEP = 0.1
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = True

def main():
    """Ana uygulama fonksiyonu"""
    try:
        setup_pyautogui()
        viewmodel = AutomationViewModel()
        app = AutomationView(viewmodel)
        app.mainloop()
    except Exception as e:
        print(f"Uygulama hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 