from django.http import HttpResponse
import assin
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import asyncio
import asyncssh
import devices


@csrf_exempt
def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        user = request.POST.get('user')
        password = request.POST.get('password')
        tipo = request.POST.get('tipo')


        try:
            if tipo == 'normal':
                loop = asyncio.new_event_loop()
                ss = loop.run_until_complete(assin.run_client(name, user, password))
                loop.close()
                print("retorno" + ss)

                if ss == "ok":
                    context = {
                        'name': "Equipment backup:: "+name+" succssesfully done!."
                    }
                else:
                    context = {
                        'name': "error" + ss
                    }
                template = loader.get_template('home.html')
                return HttpResponse(template.render(context, request))
            else:
                equipamentos= []
                loop = asyncio.new_event_loop()
                for e in devices.equipamento.keys():
                    equipamentos = [loop.create_task(assin.run_client(e, user, password))] ##Create connections asynchronously.
                    asyncio.sleep(5)
                   

                result, ss = loop.run_until_complete(asyncio.wait(equipamentos))
                loop.close()

                if ss == "ok":
                    context = {
                        'name': "Equipment backup:: "+" succssesfully done!."
                    }
                else:
                    context = {
                        'name': ss
                    }
                template = loader.get_template('home.html')
                return HttpResponse(template.render(context, request))


        except (OSerrorr, asyncssh.errorr) as exc:

            context = {
                    'name': "error:" + str(exc)
            }
            template = loader.get_template('home.html')
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('home.html')
        return HttpResponse(template.render())



