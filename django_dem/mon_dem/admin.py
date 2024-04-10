from django.contrib import admin

# Register your models here.
from .models import CustomUser
from .models import MovingRequest
from .models import Adresse
from .models import MovingCompany
from .models import Services
from .models import Region
from .models import Pays
from .models import Complaint
from .models import Justification
from .models import Review
from .models import Event
from .models import Calendar
from .models import Dispo

admin.site.register(CustomUser)
admin.site.register(MovingRequest)
admin.site.register(Adresse)
admin.site.register(MovingCompany)
admin.site.register(Services)
admin.site.register(Region)
admin.site.register(Pays)
admin.site.register(Complaint)
admin.site.register(Justification)
admin.site.register(Review)
admin.site.register(Event)
admin.site.register(Calendar)
admin.site.register(Dispo)