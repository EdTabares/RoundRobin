from operator import attrgetter
from queue import Queue
import sys
import Proceso


def validarInput(validar):
    try:
        int(validar)
        return True
    except:
        return False

        
def RoundRobin(qp):    
    listProcesosTerminados = []
    tiempoAnterior =0
    tiempoActual = 0
    intercambio = 10
    quantum = 50
    qpOrdenada = ordenarCola(qp)
    
    tiempoVuelta= 0
    promedioVuelta = 0
    promedioEspera = 0

    qpRoundRobin = Queue(cantidadProcesos)
    with open('archivo.txt', 'w') as archivo:
        archivo.write("DIAGRAMA DE GANTT")
    with open('colaListos.txt', 'w') as archivo:
        archivo.write("COLA DE LISTOS")
    print("COLA DE LISTOS\n")
    while not qpRoundRobin.empty() or tiempoActual==0:
        if tiempoActual == 0: #Esto se realiza para que obtenga de la cola de procesos a la cola de listos la primera vez
            qpRoundRobin.put(qpOrdenada.get())  
        proceso = qpRoundRobin.get() #Se extrae el proceso a trabajar de la cola de listos
        
        if not proceso.asignadoTiempoIngresoPrograma:
            proceso.tiempoIngresoPrograma = tiempoActual
            proceso.asignadoTiempoIngresoPrograma = True

        with open('colaListos.txt', 'a') as archivo:
                archivo.write("\nProceso numero: "+ str(proceso.idProceso) +" "+str(proceso.tiempoProcesador))
        tiempoAnterior = tiempoActual #Se actualiza el tiempo anterior
        tiempoActual = tiempoActual + (1*quantum+ intercambio ) #El 1*50 representa un quantum mulplicado por sus milisegundos respectivos
        
        proceso.tiempoProcesador = proceso.tiempoProcesador - 1 #Se le resta el quantum trabajado al proceso


        lenQpOrdenada= qpOrdenada.qsize()
        i=0
        while not qpOrdenada.empty() and i<= lenQpOrdenada:  #Se revisa si hay mas procesos por entrar en la cola de procesos
            pEvaluar = qpOrdenada.get() #Se extrae el siguiente proceso en orden cronologico de la lista de procesos
            #Validar si entra proceso luego de trabajar con uno
            if(tiempoActual >= pEvaluar.tiempoLlegadaMS ): #and tiempoAnterior <= pEvaluar.tiempoLlegadaMS 
                        qpRoundRobin.put(pEvaluar)  #significa que el proceso llego y debe ser añadido a la cola de listos
            else:
                 qpOrdenada.put(pEvaluar)   #el proceso aun no ha llegado por lo cual se devuelve a la espera
                 qpOrdenada = ordenarCola(qpOrdenada)   #se ordena la cola en orden de llegada
                 i = i+1      
        
        if (proceso.tiempoProcesador != 0): #se verifica si el proceso ya termino
            qpRoundRobin.put(proceso)   #si el proceso no ha terminado se vuelve a añadir a la cola de listos
            
                
        if(proceso.tiempoProcesador == 0):             
            proceso.tiempoTerminado = tiempoActual-intercambio 
            if (proceso.sumaEntradasSalida ==0):
                lenColaEs= proceso.colaEntradasSalidas.qsize()
                j=0
                while  j< lenColaEs:
                    procesoARevisarESQuantum = proceso.colaEntradasSalidas.get()
                    proceso.sumaEntradasSalida = proceso.sumaEntradasSalida  + procesoARevisarESQuantum.tiempoProcesador *quantum
                    proceso.colaEntradasSalidas.put(procesoARevisarESQuantum)
                    proceso.colaEntradasSalidas=ordenarCola(proceso.colaEntradasSalidas)
                    j = j+1
            listProcesosTerminados.append(proceso)
            if not proceso.colaEntradasSalidas.empty():
                entradaSalida =proceso.colaEntradasSalidas.get()
                tiempoDespertar = tiempoActual + entradaSalida.tiempoDormida*quantum
                
                proceso.tiempoLlegadaMS = tiempoDespertar
                proceso.tiempoProcesador = entradaSalida.tiempoProcesador

                qpOrdenada.put(proceso)
                qpOrdenada = ordenarCola(qpOrdenada)
            else:
                print("---------TIEMPOS PROCESO "+str(proceso.idProceso)+"---------\n")
                tiempoEspera = proceso.tiempoIngresoPrograma - proceso.tiempoLlegadaOriginal
                tiempoVuelta = proceso.tiempoTerminado - proceso.sumaEntradasSalida- proceso.tiempoLlegadaOriginal
                print("tiempo vuelta p:",str(proceso.idProceso),": ",str(tiempoVuelta))
                print("tiempo espera p:",str(proceso.idProceso),": ",str(tiempoEspera))
                promedioVuelta = promedioVuelta + tiempoVuelta
                promedioEspera = promedioEspera + tiempoEspera
        if(qpOrdenada.empty() and qpRoundRobin.empty()):    #Se evalua si ya todo el procedimiento termino para no poner intercambio
            tiempoActual = tiempoActual-intercambio
            intercambio = 0
            print("---------TIEMPOS PROMEDIOS ---------\n")
            print("promedio de vuelta es: "+ str(promedioVuelta/cantidadProcesos))
            print("promedio de espera es: "+ str(promedioEspera/cantidadProcesos))
        
        #print("Proceso numero: "+ str(proceso.idProceso) +" "+str(tiempoActual- intercambio)+ " " +str(1))
        with open('archivo.txt', 'a') as archivo:
            archivo.write("\n________"+str(tiempoAnterior))
            archivo.write("\n   "+str(1)+"|P"+ str(proceso.idProceso) +"|")
            archivo.write("\n________"+str(tiempoActual- intercambio))
            if not(qpOrdenada.empty() and qpRoundRobin.empty()):
                archivo.write("\n"+str(round((intercambio/quantum),2))+"|I |")
        #if not(qpOrdenada.empty() and qpRoundRobin.empty()):
            #print("Intercambio: "+ str(1/intercambio))
    #print("El algoritmo termina en el milisegundo: "+ str(tiempoActual))
    print("Cola de listos vacia")
def ordenarCola(qp):
    listCola = list(qp.queue)
    listaOrdenada = sorted(listCola, key=attrgetter('tiempoLlegadaMS'))
    qpOrdenada = Queue(cantidadProcesos)
    for proceso in listaOrdenada:
        qpOrdenada.put(proceso)
    return qpOrdenada

cantidadProcesos=0
while (cantidadProcesos<=0):
    print("Ingrese la cantidad de procesos")
    validar =input()
    if validarInput(validar):
        cantidadProcesos = int(validar)


qp = Queue(cantidadProcesos)
for i in range(cantidadProcesos):
    tiempoLlegadaMS=-1
    while (tiempoLlegadaMS<=-1):
        print("Ingrese un tiempo de llegada para el proceso {} en MS ".format(i))
        validar = input()
        if validarInput(validar):
            tiempoLlegadaMS = int(validar)
    tiempoQ =-1
    while(tiempoQ <=0):
        print("Ingrese el tiempo que requiere en quantums el proceso",i)
        validar = input()
        if validarInput(validar):
            tiempoQ = int(validar)
        
    entradaSalidaCant = -1
    while( entradaSalidaCant<=-1 ):
        print("cuantas entradas/salidas tiene el proceso ",i)
        validar = input()
        if validarInput(validar):
            entradaSalidaCant = int(validar)

    colaEntradasSalidas = Queue()        
    for j in range( entradaSalidaCant):
        entradaSalida = Proceso.EntradasSalidas()
        if(entradaSalidaCant > 0):
            dormidaPorProceso = 0
            while(dormidaPorProceso<=0):
                print("Cuanto va a dormir el proceso ",i," en QUANTUM entrada y salida #",j)
                validar = input()
                if validarInput(validar):
                    dormidaPorProceso = int(validar)

            quantumEntradaSalida = 0
            while(quantumEntradaSalida <=0):
                print("Cuantos quantum va a requerir la entrada y salida #", j)
                validar = input()
                if validarInput(validar):
                    quantumEntradaSalida = int(validar)
                        
            entradaSalida.idEntradaSalida = j                          
            entradaSalida.tiempoDormida = dormidaPorProceso
            entradaSalida.tiempoProcesador = quantumEntradaSalida

            colaEntradasSalidas.put(entradaSalida)
    proceso = Proceso.Proceso(i, tiempoLlegadaMS, tiempoQ, colaEntradasSalidas)
    qp.put(proceso)

RoundRobin(qp)









#while not qpOrdenada.empty():
    #print(qpOrdenada.get().idProceso)


