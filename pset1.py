
# Imports permitidos (não utilize nenhum outro import!):
import sys
import math
import base64
import tkinter
from io import BytesIO
from PIL import Image as PILImage

# Classe Imagem:


class Imagem:
    def __init__(self, largura, altura, pixels):
        self.largura = largura
        self.altura = altura
        self.pixels = pixels

    # Seleciona a cor do pixel

    def get_pixel(self, x, y):
        if x >= 0 and y >= 0 and x < self.largura and y < self.altura:
            return self.pixels[x + self.largura * y]
        # Caso x seja maior ou menor que os limites, x e y será igual aos limites.
        # Isso foi feito para resolver o problema das bordas nos calculos com o kernel
        else:
            if x < 0:
                x = 0
            elif y < 0:
                y = 0
            if x >= self.largura:
                x = self.largura - 1
            elif y >= self.altura:
                y = self.altura - 1
            # No fim, é usado da recursividade para pegar a cor do pixel atual, mas agora com a posição corrigida
            return self.get_pixel(x, y)

    # Define uma cor ao pixel selecionado
    def set_pixel(self, x, y, c):
        self.pixels[x + self.largura * y] = c

    # Função para arredondar a cor para o inteiro mais proximo, e limita-la entre 0 e 255
    def arredondar(self, c):
        c = round(c)
        if c < 0:
            c = 0
        elif c > 255:
            c = 255
        return c

    # Aplica a função do parâmetro para cada pixel na imagem, nesse caso é usada apenas na função invertida()
    def aplicar_por_pixel(self, func):
        resultado = Imagem.nova(self.largura, self.altura)
        for y in range(resultado.altura):
            for x in range(resultado.largura):
                cor = self.get_pixel(x, y)
                nova_cor = func(cor)
                resultado.set_pixel(x, y, nova_cor)
        return resultado

    # Aplica um kernel passado como parametro, para todos os pixels da imagem
    def correlacao(self, kernel, arredondar=1):
        # Tamanho do lado do kernel
        kernel_tamanho = int(math.sqrt(len(kernel)))

        resultado = Imagem.nova(self.largura, self.altura)
        for y in range(resultado.altura):
            for x in range(resultado.largura):
                somatorio = 0
                for kernel_y in range(kernel_tamanho):
                    for kernel_x in range(kernel_tamanho):
                        # Atribui a cor do pixel, na posição da soma do pixel atual da imagem(x ou y) e a posição atual do kernel(kernel_x ou kernel_y),
                        # e subtraindo o centro do kernel(kernel_tamanho // 2)
                        cor = self.get_pixel(
                            x + kernel_x - kernel_tamanho // 2, y + kernel_y - kernel_tamanho // 2)
                        somatorio += cor * \
                            kernel[kernel_y * kernel_tamanho + kernel_x]
                # Para algumaas funções, o valor não pode ser arredondado no momento da correlação pois pode ser necessário fazer mais operações com o resultado da correlação (nesse caso a função bordas())
                # Então, no inicio da função é passado arredondar=1 como parametro padrão, mas em caso de uma correlação que não possa ter o resultado arredondado, é possivel chama-la com arredondar=0
                if arredondar == 1:
                    somatorio = self.arredondar(somatorio)
                resultado.set_pixel(x, y, somatorio)
        return resultado

    # Inverte a imagem usando o complemento da cor para chegar a 255

    def invertida(self):
        return self.aplicar_por_pixel(lambda c: 255 - c)

    def borrada(self, n):
        # Cria um kernel com tamanho n onde o valor de todas as posições é 1/n**2
        kernel = []
        for i in range(n**2):
            kernel.append(1/n**2)

        return self.correlacao(kernel)

    def focada(self, n):
        kernel_tamanho = n**2
        # Cria o kernel de identidade
        kernel_i = []
        for i in range(kernel_tamanho):
            if (i == n**2 // 2):
                kernel_i.append(1)
            else:
                kernel_i.append(0)
        # Cria o kernel borrar
        kernel_b = []
        for i in range(kernel_tamanho):
            kernel_b.append(1/n**2)
        # Cria o kernel resultado
        kernel = []
        for i in range(kernel_tamanho):
            kernel.append(2 * kernel_i[i] - kernel_b[i])

        return self.correlacao(kernel)

    def bordas(self):
        kernel_x = [-1, 0, 1,
                    -2, 0, 2,
                    -1, 0, 1,]

        kernel_y = [-1, -2, -1,
                    0, 0, 0,
                    1, 2, 1,]

        # Aplica o kernel de borda apenas em x
        Ox = self.correlacao(kernel_x, 0)
        # Aplica o kernel de borda apenas em y
        Oy = self.correlacao(kernel_y, 0)
        resultado = Imagem.nova(self.largura, self.altura)

        for y in range(resultado.altura):
            for x in range(resultado.largura):
                # Une kernel_x e kernel_y em uma nova imagem
                Oxy = self.arredondar(
                    math.sqrt(Ox.get_pixel(x, y)**2 + Oy.get_pixel(x, y)**2))
                resultado.set_pixel(x, y, Oxy)

        return resultado

    # Abaixo deste ponto estão utilitários para carregar, salvar e mostrar
    # as imagens, bem como para a realização de testes. Você deve ler as funções
    # abaixo para entendê-las e verificar como funcionam, mas você não deve
    # alterar nada abaixo deste comentário.
    #
    # ATENÇÃO: NÃO ALTERE NADA A PARTIR DESTE PONTO!!! Você pode, no final
    # deste arquivo, acrescentar códigos dentro da condicional
    #
    #                 if __name__ == '__main__'
    #
    # para executar testes e experiências enquanto você estiver executando o
    # arquivo diretamente, mas que não serão executados quando este arquivo
    # for importado pela suíte de teste e avaliação.

    def __eq__(self, other):
        return all(getattr(self, i) == getattr(other, i)
                   for i in ('altura', 'largura', 'pixels'))

    def __repr__(self):
        return "Imagem(%s, %s, %s)" % (self.largura, self.altura, self.pixels)

    @classmethod
    def carregar(cls, nome_arquivo):
        """
        Carrega uma imagem do arquivo fornecido e retorna uma instância dessa
        classe representando essa imagem. Também realiza a conversão para tons
        de cinza.

        Invocado como, por exemplo:
           i = Imagem.carregar('test_images/cat.png')
        """
        with open(nome_arquivo, 'rb') as guia_para_imagem:
            img = PILImage.open(guia_para_imagem)
            img_data = img.getdata()
            if img.mode.startswith('RGB'):
                pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                          for p in img_data]
            elif img.mode == 'LA':
                pixels = [p[0] for p in img_data]
            elif img.mode == 'L':
                pixels = list(img_data)
            else:
                raise ValueError('Modo de imagem não suportado: %r' % img.mode)
            l, a = img.size
            return cls(l, a, pixels)

    @classmethod
    def nova(cls, largura, altura):
        """
        Cria imagens em branco (tudo 0) com a altura e largura fornecidas.

        Invocado como, por exemplo:
            i = Imagem.nova(640, 480)
        """
        return cls(largura, altura, [0 for i in range(largura * altura)])

    def salvar(self, nome_arquivo, modo='PNG'):
        """
        Salva a imagem fornecida no disco ou em um objeto semelhante a um arquivo.
        Se o nome_arquivo for fornecido como uma string, o tipo de arquivo será
        inferido a partir do nome fornecido. Se nome_arquivo for fornecido como
        um objeto semelhante a um arquivo, o tipo de arquivo será determinado
        pelo parâmetro 'modo'.
        """
        saida = PILImage.new(mode='L', size=(self.largura, self.altura))
        saida.putdata(self.pixels)
        if isinstance(nome_arquivo, str):
            saida.save(nome_arquivo)
        else:
            saida.save(nome_arquivo, modo)
        saida.close()

    def gif_data(self):
        """
        Retorna uma string codificada em base 64, contendo a imagem
        fornecida, como uma imagem GIF.

        Função utilitária para tornar show_image um pouco mais limpo.
        """
        buffer = BytesIO()
        self.salvar(buffer, modo='GIF')
        return base64.b64encode(buffer.getvalue())

    def mostrar(self):
        """
        Mostra uma imagem em uma nova janela Tk.
        """
        global WINDOWS_OPENED
        if tk_root is None:
            # Se Tk não foi inicializado corretamente, não faz mais nada.
            return
        WINDOWS_OPENED = True
        toplevel = tkinter.Toplevel()
        # O highlightthickness=0 é um hack para evitar que o redimensionamento da janela
        # dispare outro evento de redimensionamento (causando um loop infinito de
        # redimensionamento). Para maiores informações, ver:
        # https://stackoverflow.com/questions/22838255/tkinter-canvas-resizing-automatically
        tela = tkinter.Canvas(toplevel, height=self.altura,
                              width=self.largura, highlightthickness=0)
        tela.pack()
        tela.img = tkinter.PhotoImage(data=self.gif_data())
        tela.create_image(0, 0, image=tela.img, anchor=tkinter.NW)

        def ao_redimensionar(event):
            # Lida com o redimensionamento da imagem quando a tela é redimensionada.
            # O procedimento é:
            #  * converter para uma imagem PIL
            #  * redimensionar aquela imagem
            #  * obter os dados GIF codificados em base 64 (base64-encoded GIF data)
            #    a partir da imagem redimensionada
            #  * colocar isso em um label tkinter
            #  * mostrar a imagem na tela
            nova_imagem = PILImage.new(
                mode='L', size=(self.largura, self.altura))
            nova_imagem.putdata(self.pixels)
            nova_imagem = nova_imagem.resize(
                (event.width, event.height), PILImage.NEAREST)
            buffer = BytesIO()
            nova_imagem.save(buffer, 'GIF')
            tela.img = tkinter.PhotoImage(
                data=base64.b64encode(buffer.getvalue()))
            tela.configure(height=event.height, width=event.width)
            tela.create_image(0, 0, image=tela.img, anchor=tkinter.NW)

        # Por fim, faz o bind da função para que ela seja chamada quando a tela
        # for redimensionada:
        tela.bind('<Configure>', ao_redimensionar)
        toplevel.bind('<Configure>', lambda e: tela.configure(
            height=e.height, width=e.width))

        # Quando a tela é fechada, o programa deve parar
        toplevel.protocol('WM_DELETE_WINDOW', tk_root.destroy)


# Não altere o comentário abaixo:
# noinspection PyBroadException
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()

    def refaz_apos():
        tcl.after(500, refaz_apos)

    tcl.after(500, refaz_apos)
except:
    tk_root = None

WINDOWS_OPENED = False


if __name__ == '__main__':
    # O código neste bloco só será executado quando você executar
    # explicitamente seu script e não quando os testes estiverem
    # sendo executados. Este é um bom lugar para gerar imagens, etc.

    # O código a seguir fará com que as janelas de Imagem.mostrar
    # sejam exibidas corretamente, quer estejamos executando
    # interativamente ou não:

    # Testes

    img = Imagem(0, 0, 0)
    i = img.carregar('./test_images/pigbird.png')

    i.mostrar()
    i.invertida().mostrar()
    i.focada(3).mostrar()
    i.borrada(3).mostrar()
    i.bordas().mostrar()

    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()
