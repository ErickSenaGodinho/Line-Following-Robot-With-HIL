# Trabalho de Sistemas Embebidos (2024)

Este repositório contém o trabalho desenvolvido na disciplina de **Sistemas Embebidos** do **IPB - Instituto Politécnico de Bragança**.

## Objetivo

Desenvolver um sistema de controlo para um robô móvel com **ESP32**, capaz de seguir uma linha num ambiente simulado no **Webots**, corrigindo automaticamente a trajetória sempre que se desviar.

## Descrição

O robô utiliza sensores (simulados) para detectar a linha e ajustar o movimento em tempo real. Quando perde a linha, executa uma rotina de correção até reencontrá-la, continuando o percurso de forma autónoma.

O projeto suporta dois modos de execução:
- **Com ESP32** (Hardware-in-the-Loop - HIL)  
- **Sem ESP32** (simulação completa no Webots)  

## Demonstração

**Execução do robô seguindo linha:**

![Demonstração](./following-line-robot.gif)

## Tecnologias

- Python  
- ESP32  
- Webots  

## Estrutura do Projeto

- `/worlds` -> Ambiente de simulação
- `/controllers` -> Scripts de controlo do robô

### Controllers

- `main.py` → Script principal  
- `line_following_with_HIL.py` → Execução com ESP32 (HIL)  
- `line_following_without_ESP32.py` → Execução sem hardware  

## HIL (Hardware-in-the-Loop)

HIL é uma abordagem que combina **hardware real** (ESP32) com **simulação** (Webots), permitindo testes mais realistas sem necessidade de um sistema físico completo.

## Execução

1. Abrir o Webots  
2. Carregar um mundo da pasta `/worlds`  
3. Selecionar um controlador da pasta `/controllers`:
   - Com ESP32 → `line_following_with_HIL.py`  
   - Sem ESP32 → `line_following_without_ESP32.py`  

## Autor

Erick Sena Godinho  
