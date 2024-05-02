from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from paciente.models import Consulta, Documentos
from django.contrib.auth.decorators import login_required


def cadastro_medico(request):
    
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já possui um cadastro como médico')
        return redirect('/medicos/abrir_horario')

    if request.method == 'GET':
        especialidades = Especialidades.objects.all()
        context = {'especialidades': especialidades,
                   'is_medico':is_medico(request.user)
                   }
        return render(request, 'cadastro_medico.html', context)
    elif request.method == 'POST':
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        dados_medico = DadosMedico(
            crm = crm,
            nome = nome,
            cep = cep,
            rua = rua,
            bairro = bairro,
            numero = numero,
            cedula_identidade_medica = cim,
            rg = rg,
            foto_perfil = foto,
            especialidade_id = especialidade,
            descricao = descricao,
            valor_consulta = valor_consulta,
            user = request.user

        )

        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso!')
        return redirect('/medicos/abrir_horario')


@login_required
def abrir_horario(request):
    
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página')
        return redirect('/usuarios/logout')
    
    if request.method == 'GET':
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        print(datas_abertas)
        context = {'dados_medicos':dados_medicos,
                   'datas_abertas':datas_abertas,
                   'is_medico':is_medico(request.user)
                   }
        return render(request, 'abrir_horario.html', context)
    elif request.method == 'POST':
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")
        
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data não pode ser mais antiga que a data atual')
            return redirect('/medicos/abrir_horario')
        
        horario_abrir = DatasAbertas(
            data = data,
            user = request.user,
        )

        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS, 'Data aberta com sucesso.')
        return redirect('/medicos/abrir_horario')

@login_required    
def consultas_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página')
        return redirect('/usuarios/logout')
    
    hoje = datetime.now().date()
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)

    context = {
        'consultas_hoje':consultas_hoje,
        'consultas_restantes':consultas_restantes,
        'is_medico':is_medico(request.user)
        }

    return render(request, 'consultas_medico.html', context)

@login_required
def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página')
        return redirect('/usuarios/logout')
    
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documentos.objects.filter(consulta=consulta)
        context = {
            'consulta':consulta,
            'is_medico':is_medico(request.user),
            'documentos':documentos
        }
        return render(request, 'consulta_area_medico.html', context)
    
    elif request.method == 'POST':
        link_consulta = request.POST.get('link')
        consulta_atual = Consulta.objects.get(id=id_consulta)

        if consulta_atual.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta foi cancelada')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif consulta_atual.status == 'F':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        if not link_consulta:
            messages.add_message(request, constants.WARNING, 'Insira um link válido para a consulta')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        
        consulta_atual.link = link_consulta
        consulta_atual.status = 'I'
        consulta_atual.save()
        messages.add_message(request, constants.SUCCESS, 'Essa consulta inicializada')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

@login_required
def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página')
        return redirect('/usuarios/logout')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if not request.user == consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua')
        return redirect(f'/medicos/consultas_medico/')
    consulta.status = 'F'
    consulta.save()
    
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

@login_required
def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página')
        return redirect('/usuarios/logout')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if not request.user == consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua')
        return redirect(f'/medicos/consultas_medico/')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.ERROR, 'Preencha o campo documento')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    documento = Documentos(
        consulta = consulta,
        titulo = titulo,
        documento = documento
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    

