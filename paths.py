import os
import sys

def get_resource_path(rel_path=""):
    """
    Dondurulmuş exe içindeki gömülü varlıkların (assets) yolunu döndürür.
    Geliştirme modunda kaynak klasörü kullanır.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, rel_path) if rel_path else base_path

def get_data_dir():
    """
    Kullanıcının yapılandırma (config.json) ve görev (tasks.json) verilerinin
    kalıcı olarak saklanacağı merkezi klasörü döndürür.
    Tüm Windows sistem standartlarına uygun olarak %APPDATA%/ToOoDo klasörünü kullanır.
    Böylece exe nereye taşınırsa taşınsın veya yeni sürüm derlendiğinde notlar asla kaybolmaz.
    """
    appdata = os.getenv("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    target = os.path.join(appdata, "ToOoDo")
    os.makedirs(target, exist_ok=True)
    return target
