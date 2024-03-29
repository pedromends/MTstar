##################################################
##      MTStar - Máquina de Turing Doravante    ##
##      João Pedro Mendonça de Souza - 0035330  ##
##      Teoria da Computação - 2022             ##
###################################################


from interface import *
from memoria import *


class TuringMachine:
    maxPassosSemIntervencao = 1000

    def __init__(self, arquivo, entrada, resume=True, debug=False, steps=0):
        self.interface = Interface(arquivo, entrada, resume, debug, steps)
        self.memoriaX = Memoria('Fita X')
        self.memoriaY = Memoria('Fita Y')
        self.memoriaZ = Memoria('Fita Z')
        self.estado = None
        self.pilhaDeChamada = list()
        self.blocos = None
        if debug != '':
            self.log = open(debug, "w")
        return

    def carregaPrograma(self):
        carga = self.interface.entrada()
        self.entrada = carga['entrada']
        self.resume = carga['resume']
        self.debug = carga['debug']
        self.steps = carga['steps']
        self.blocos = carga['blocos']
        if self.debug != '':
            self.log.write("Relatório de saída:\n\n")

    def executa(self):
        self.memoriaX.carregaPalavra(self.entrada)
        print("Simulador de Máquina de Turing Suave versão 1.0")
        print("Desenvolvido como trabalho prático para a disciplina de Teoria da Computação")
        print("Autor: João Pedro Mendonça de Souza, IFMG − Formiga, 2022.")
        self.chamada('main', None)
        self.run()
        return

    def chamada(self, bloco, retorno):
        try:
            inicial, comandos = self.blocos[bloco]
        except:
            print('Erro... bloco %s não encontrado' % bloco)
            raise SystemExit

        self.estado = inicial
        self.empilhaChamada(bloco, retorno)

    def empilhaChamada(self, bloco, retorno):
        if retorno == 'retorne':
            print('Erro... duplo retorno a chamada do bloco %s' % bloco)
            raise SystemExit

        self.pilhaDeChamada.append([bloco, retorno])

    def desempilhaChamada(self):
        self.pilhaDeChamada = self.pilhaDeChamada[0:-1]

    def run(self):
        self.resetaPassos()
        self.running = True
        self.aceita = False

        while self.running:
            comando = self.buscaComando()
            self.executaComando(comando)

        if self.aceita:
            print("Configuração Instantânea Final")
            self.memoriaX.dump()
            self.memoriaY.dump()
            self.memoriaZ.dump()
            print('\nACEITA.')
        else:
            print('\nREJEITA.')

    def resetaPassos(self):
        if self.steps == 0:
            self.steps = TuringMachine.maxPassosSemIntervencao
        self.passos = self.steps

    def buscaComando(self):  # uma parte busca comando, a outra executa, esse busca
        bloco = self.blocoAtual()
        estado = self.estado
        fita1 = self.memoriaX.leFita1()
        fitaEspecial = self.memoriaX.leFita2()
        fita2 = self.memoriaY.leFita1()
        fita3 = self.memoriaZ.leFita1()
        inicial, comandos = self.blocos[bloco]

        for c in comandos:
            state = c[1]  # estado igual primeira posição do vetor de comando
            if state != estado:
                continue

            tipo = c[0]
            if tipo == 'fita1' and c[3] in (fita1, '*'):
                return c
            if tipo == 'fita2' and c[3] in (fita2, '*'):
                return c
            if tipo == 'fita3' and c[3] in (fita3, '*'):
                return c
            if tipo == 'fitaEspecial' and c[3] in (fitaEspecial, '*'):
                return c
            if tipo == 'chamada':
                return c
            if tipo == 'final':
                return c
            if tipo == 'colar':
                return c
            if tipo == 'copiar':
                return c
            if tipo == 'gravar':
                return c

    def blocoAtual(self):  # bloco atual é sempre a ultima posição da pilha de chamada
        return self.pilhaDeChamada[(-1)][0]  # primeira posição da ultima chamada de bloco

    def executaComando(self, c):
        if c is None:
            self.terminouExecucao(False)

        parada = False
        self.debuga(c, parada)
        tipo = c[0]

        if tipo == 'fita1' or tipo == 'fita2' or tipo == 'fita3':

            t, estadoIni, fitaLer, charLer, dirFitaLer, estadoAlvo, fitaEscrita, charEscrita, dirFitaEscrita = c

            if charEscrita != '*':  # se o novo caracter for diferente do coringa, escreve na fita o novo caracter

                if fitaEscrita == 'X':
                    self.memoriaX.escreveFita1(charEscrita)
                    self.memoriaX.moveFita1(dirFitaEscrita)
                elif fitaEscrita == 'Y':
                    self.memoriaY.escreveFita1(charEscrita)
                    self.memoriaY.moveFita1(dirFitaEscrita)
                elif fitaEscrita == 'Z':
                    self.memoriaZ.escreveFita1(charEscrita)
                    self.memoriaZ.moveFita1(dirFitaEscrita)

            elif charEscrita == '*':
                if fitaEscrita == 'X':
                    self.memoriaX.moveFita1(dirFitaEscrita)
                elif fitaEscrita == 'Y':
                    self.memoriaY.moveFita1(dirFitaEscrita)
                elif fitaEscrita == 'Z':
                    self.memoriaZ.moveFita1(dirFitaEscrita)

            if fitaLer == 'X' and fitaEscrita != 'X':
                self.memoriaX.moveFita1(dirFitaLer)

            elif fitaLer == 'Y' and fitaEscrita != 'Y':
                self.memoriaY.moveFita1(dirFitaLer)

            elif fitaLer == 'Z' and fitaEscrita != 'Z':
                self.memoriaZ.moveFita1(dirFitaLer)

            self.atualizaEstado(estadoAlvo)

        elif tipo == 'fitaEspecial':
            t, estadoIni, fitaLer, charLer, dirFitaLer, estadoAlvo, fitaEscrita, charEscrita, dirFitaEscrita = c
            if charEscrita != '*':  # se o novo caracter for coringa, não escreve nada
                self.memoriaX.escreveFita1(charEscrita)

            self.memoriaX.moveFita1(dirFitaEscrita)
            self.atualizaEstado(estadoAlvo)

        elif tipo == 'chamada':
            t, estadoIni, idBlocoAlvo, estadoRetorno = c
            self.chamada(idBlocoAlvo, estadoRetorno)

        elif tipo == 'final':
            tipo, estadoAlvo, comando = c
            self.atualizaEstado(comando)

        if tipo == 'colar':
            tipo, estadoIni, comando, estadoRetorno = c
            car = self.memoriaX.leFita2()
            self.memoriaX.escreveFita1(car)
            self.atualizaEstado(estadoRetorno)

        elif tipo == 'copiar':
            tipo, estadoIni, comando, estadoRetorno = c
            car = self.memoriaX.leFita1()
            self.memoriaX.escreveFita2(car)
            self.atualizaEstado(estadoRetorno)

        elif tipo == 'gravar':
            estado, tipo, car, alvo = c
            self.memoriaX.escreveFita2(car)
            self.atualizaEstado(alvo)

    def atualizaEstado(self, novoEstado):
        if novoEstado == 100:
            print("Pare")

        if novoEstado == 'retorne':
            bloco, retorno = self.pilhaDeChamada[(-1)]
            if retorno is None:
                self.terminouExecucao()
            else:
                self.estado = retorno
                self.desempilhaChamada()

        elif novoEstado == 'aceite':
            self.terminouExecucao(True)

        elif novoEstado == 'rejeite':
            self.terminouExecucao(False)

        else:
            self.estado = novoEstado

        return

    def terminouExecucao(self, aceita=False):
        self.aceita = aceita
        self.running = False

    def debuga(self, c, parada):
        interrompeu = False
        while self.passos <= 0:
            interrompeu = True

            print('\nEste programa executou %d computações.' % self.steps + '\nDeseja continuar?' +'\nDigite um inteiro para mais n passos.' + '\n(0 = stop, %d = max) ' % TuringMachine.maxPassosSemIntervencao)

            while True:
                try:
                    n = input('--> ')
                except SyntaxError:
                    n = -1
                else:
                    try:
                        n = int(n)
                    except ValueError:
                        n = -1
                    else:
                        if 0 <= int(n) <= TuringMachine.maxPassosSemIntervencao:
                            break

            self.steps = self.passos = int(n)
            if self.steps == 0:
                self.terminouExecucao(False)
                return

        if parada and not interrompeu:
            try:
                input('\nBreakpoint... pressione [enter] para continuar \n')
            except SyntaxError:
                pass

        if not self.debug:
            self.passos = int(self.passos) - 1
            return

        linhaX = 'Fita X: '
        linhaX += self.montaLinha()
        linhaX = linhaX + str(self.memoriaX)

        linhaY = 'Fita Y: '
        linhaY += self.montaLinha()
        linhaY = linhaY + str(self.memoriaY)

        linhaZ = 'Fita Z: '
        linhaZ += self.montaLinha()
        linhaZ = linhaZ + str(self.memoriaZ)

        if not self.resume:
            print(linhaX, ' | ', c)
            print(linhaY, ' |')
            print(linhaZ, ' | \n')

        if self.debug != '':
            self.log.write(linhaX + ' | ' + str(c) + '\n')
            self.log.write(linhaY + '\n')
            self.log.write(linhaZ + '\n\n')

        self.passos = int(self.passos) - 1

    def numComandoExecutado(self):
        n = self.steps
        if n == 0:
            n = TuringMachine.maxPassosSemIntervencao
        n = n - self.passos + 1
        return n

    def montaLinha(self):
        linha = '{:0>3d} '.format(self.numComandoExecutado())
        linha = linha + '{:.>15}.'.format(self.blocoAtual())
        linha = linha + '{:0>4d} : '.format(int(self.estado))
        return linha


if __name__ == '__main__':
    parametros = vars(linhaDeComando())
    MT = TuringMachine(**parametros)
    MT.carregaPrograma()
    MT.executa()
    print("FIM DA SIMULAÇÃO")

    # O padrão de invocação é: simuladorMT.py [-h] [-step STEP] [-resume] [-debug] arquivo entrada
    # Alguns possíveis comandos para invocar a Máquina de Turing são:
    # python3 simuladorMT.py -help                             |   mostra como a linha de comando funciona
    # python3 simuladorMT.py -debug log.txt somaV1.mt 10+10=   |   mostra a execução passo a passo no console e a registra no arquivo
    # python3 simuladorMT.py -resume somaV1.mt 10+10=          |   mostra apenas o resultado final e é a opção padrão caso nenhuma seja selecionada
    # python3 simuladorMT.py -steps 50 somaV1.mt 10+10=        |   executa 50 passos e pergunta pro usuario quantas computações fazer, esse número pode variar de 1 até 1000
