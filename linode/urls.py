
from django.urls import path, include
from .views import listVMClass, viewVM, startVM, extendVM, terminateVM, restartVM, runcron

urlpatterns = [
    path('list', listVMClass),
    path('view/<int:id>', viewVM, name='viewVM'),
    path('start/<int:classId>', startVM, name='startVM'),
    path('extend/<int:classId>', extendVM, name='extendVM'),
    path('stop/<int:classId>', terminateVM, name='stopVM'),
    path('restart/<int:classId>/<int:vmId>', restartVM, name='restartVM'),
    path('cleanup', runcron, name='cleanup'),
]
