class Constants:
    def __init__(self):
        # Renkler
        self.COLORS = {
            'bg': '#f0f0f0',
            'text': '#333333',
            'primary': '#2196F3',
            'success': '#4CAF50',
            'danger': '#F44336',
            'warning': '#FFC107',
            'disabled': '#9E9E9E',
        }
        
        # Yazı tipi ayarları
        self.STYLES = {
            'font_family': 'Segoe UI',
            'header_font_size': 10,
            'text_font_size': 9,
            'button_font_size': 10,
        }
        
        # Koordinat ayarları
        self.COORDINATES = {
            'max_count': 20,
            'default_delay': 0.5,
        }
        
        # Mesajlar
        self.MESSAGES = {
            'exit_confirm': 'Uygulamadan çıkmak istediğinize emin misiniz?',
            'new_file_confirm': 'Tüm veriler silinecek. Emin misiniz?',
            'invalid_loop_count': 'Geçerli bir döngü sayısı giriniz!',
            'file_load_error': 'Dosya açılırken bir hata oluştu!',
            'file_save_error': 'Dosya kaydedilirken bir hata oluştu!',
        } 