from fastapi.templating import Jinja2Templates

# Создаем один глобальный экземпляр для всего приложения
templates = Jinja2Templates(directory="templates")
