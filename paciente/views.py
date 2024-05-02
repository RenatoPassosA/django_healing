from django.shortcuts import render, redirect
from datetime import datetime
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from .models import Consulta, Documentos
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.method == 'GET':
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedico.objects.all()

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

        especialidades = Especialidades.objects.all()
        context = {'medicos':medicos,
                   'especialidades':especialidades,
                   'is_medico':is_medico(request.user)
                   }
        return render(request, 'home.html', context)

@login_required
def escolher_horario(request, id_dados_medicos):
    if request.method == 'GET':
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user = medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        context = {
            'medico':medico,
            'datas_abertas':datas_abertas,
            'is_medico':is_medico(request.user)
        }
        return render(request, 'escolher_horario.html', context)

@login_required
def agendar_horario(request, id_datas_abertas):
     if request.method == 'GET':
        data_aberta = DatasAbertas.objects.get(id = id_datas_abertas)

        horario_agendado= Consulta(
             paciente = request.user,
             data_aberta = data_aberta
         )

        horario_agendado.save()
        data_aberta.save()

        messages.add_message((request), constants.SUCCESS, 'Consulta agendada com sucesso. ')
        return redirect('/pacientes/minhas_consultas/')

@login_required     
def minhas_consultas(request):
    minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
    especialidades_filtrar = request.GET.get("especialidade")
    data_filtrar = request.GET.get("data")
   
    if especialidades_filtrar:
        minhas_consultas = minhas_consultas.filter(data_aberta__user__dadosmedico__especialidade__id=especialidades_filtrar)
        

    if data_filtrar:
        minhas_consultas = minhas_consultas.filter(data_aberta__data__gte=data_filtrar)
        

    especialidades = Especialidades.objects.all()
    
    print(data_filtrar)

    context = {
    'minhas_consultas':minhas_consultas,
    'is_medico':is_medico(request.user),
    'especialidades':especialidades
    }
    return render(request, 'minhas_consultas.html', context)
  
        
    

@login_required
def consulta(request, id_consulta):
    if request.method =='GET':
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        documentos = Documentos.objects.filter(consulta=consulta)
        context = {
            'consulta':consulta,
            'dado_medico':dado_medico,
            'documentos':documentos
        }
        return render(request, 'consulta.html', context)

@login_required    
def cancelar_consulta(request, id_consulta):
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.paciente:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua')
        return redirect(f'/pacientes/consulta/{id_consulta}')
    
    consulta.status = 'C'
    consulta.save()
    return redirect(f'/pacientes/consulta/{id_consulta}')