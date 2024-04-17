from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib import auth

    
def cadastro(request):
    if request.method == 'GET': #se minha requisição for feita pelo navegador
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, "A senha e a confirmação devem ser iguais")
            return redirect('/usuarios/cadastro/')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, "A senha deve possuir mais de 6 caracteres")
            return redirect('/usuarios/cadastro/')
        
        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR, "O usuário já existe")
            return redirect('/usuarios/cadastro/')
        
        user = User.objects.create_user( #o que está na esquerda é o campo do database e a direita é a variavel acima que salva os valores
            username=username,
            email = email,
            password = senha

        )
        
        return HttpResponse(f'Usuário criado com sucesso')
    

def login_view(request):
    if request.method == "GET":
        print(request.user)
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username') #lembrando que dentro do .get é o name dado no input do form correspondente ao campo
        senha = request.POST.get('senha')


        user = auth.authenticate(request, username=username, password=senha)
        if user:
            auth.login(request, user)
            return redirect('/pacientes/home')
        
        messages.add_message(request, constants.ERROR, "Usuário ou senha inválidos")
        return redirect('/usuarios/login/')
    

def logout(request):
    auth.logout(request)
    return redirect('/usuarios/login')