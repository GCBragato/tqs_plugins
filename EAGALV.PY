# coding: ISO-8859-1
#-----------------------------------------------------------------------------
#    EAGALV.PY    Menu de Python para ALVEST desenvolvido por BRGT Engenharia
#    de estruturas. Instagram @brgt.estruturas
#-----------------------------------------------------------------------------
from sys import path as sys_path
sys_path.append(r"C:\TQSW\EXEC\PYTHON\resources\codes")
from TQS import TQSDwg, TQSEag
import alvest_blocks as ab
import math


def get_alv_blocks(tqsjan):
    """Detecta todos os blocos ALV existentes"""

    # Iterador para detectar e salvar os blocos grauteados
    my_layers = [241, 245]
    myBlocks = []
    tqsjan.dwg.iterator.Begin()
    while True:
        itipo = tqsjan.dwg.iterator.Next()
        #Se ? bloco
        if itipo == TQSDwg.DWGTYPE_BLOCK:
            #Se est? nas layers listadas
            if tqsjan.dwg.iterator.level in my_layers:
                # Extrai o nome do bloco
                blockName = tqsjan.dwg.iterator.blockName
                # Se nome do bloco maior que 5 (grauteado), salva
                if len(blockName) > 5:
                    addr = tqsjan.dwg.iterator.GetElementReadPosition()
                    blockName = blockName
                    x = tqsjan.dwg.iterator.x1
                    y = tqsjan.dwg.iterator.y1
                    xScale = tqsjan.dwg.iterator.xScale
                    yScale = tqsjan.dwg.iterator.yScale
                    insertAngle = tqsjan.dwg.iterator.insertAngle
                    level = tqsjan.dwg.iterator.level
                    myBlocks.append(
                        [addr,blockName,x,y,xScale,yScale,insertAngle,level]
                        )
        # Se ? fim do arquivo, sair do loop
        if itipo == TQSDwg.DWGTYPE_EOF:
            break
    return myBlocks


def remove_graute (eag, tqsjan):
    """Remove Pontos de Graute existentes"""
    # Detec??o de todos os blocos com pontos de graute
    my_blocks = get_alv_blocks(tqsjan)
    # Corre??o de nome do bloco
    for block in my_blocks:
        block[1] = block[1][0:5]
    # Deletar blocos grauteados e insere sem graute
    for block in my_blocks:
        tqsjan.dwg.draw.level = block[7]
        tqsjan.dwg.draw.BlockInsert(block[1],block[2],block[3],block[4],block[5],block[6])
        tqsjan.dwg.edit.Erase(block[0])
    tqsjan.Regen()


def coords_graute (eag,blocks):
    """Coordenadas dos grautes"""
    # Corre��o de rota��o para escala X negativa
    for block in blocks:
        if block[4] < 0:
            block[6] = block[6] + 180
            if block[6] > 360:
                block[6] = block[6] - 360
            block[4] = abs(block[4])

    # C�lculo da posi��o do graute para cada bloco
    coords = []
    dict_fam = ab.dict_fam()
    for block in blocks:
        block_data = dict_fam[block[1]]
        angle = math.radians(block[6])
        for graute_cg in block_data.xyseptCG:
            x = graute_cg[0]
            y = graute_cg[1]
            x_graute = round(x*math.cos(angle) - y*math.sin(angle),6)
            y_graute = round(x*math.sin(angle) + y*math.cos(angle),6)
            x_barra = block[2] + x_graute
            y_barra = block[3] + y_graute
            coords.append([x_barra,y_barra])
    return coords


def insere_arm_vert(eag, tqsjan):
    """Insere armaduras verticais nos grautes existentes"""

    # Escolha qual o tipo de armadura a ser inserida
    eag.exec.Command('ID_PTFER_ATUAL')
    eag.entry.KeyEscape()

    # Detec��o de todos os blocos com pontos de graute
    my_blocks = get_alv_blocks(tqsjan)
    # Coordenadas dos grautes
    coords = coords_graute(eag,my_blocks)

    # Insere armaduras verticais
    for coord in coords:
        eag.exec.Command('ID_PTFER_INSR')
        eag.entry.Point(coord[0],coord[1])
    eag.exec.Command('ID_PTFER_INSR')
    eag.entry.Point(coords[-1][0],coords[-1][1])
