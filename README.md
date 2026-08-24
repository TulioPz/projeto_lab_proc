# Requisitos do Projeto – Sistema de Controle de Acesso Veicular

## 1. Descrição Geral

O projeto consiste no desenvolvimento de um **sistema de controle de acesso de veículos para um estacionamento corporativo**, utilizando uma Raspberry Pi

O sistema deverá permitir que veículos autorizados entrem no estacionamento por meio da identificação de uma **tag RFID**. Durante o período noturno, será exigida uma camada adicional de segurança por meio de uma **senha digitada em teclado matricial**.

Após a autorização da entrada, um servomotor deverá simular o acionamento da cancela. Um sensor ultrassônico será utilizado para identificar a passagem do veículo e permitir o fechamento seguro da cancela.

O sistema também deverá manter o controle dos veículos presentes no estacionamento, utilizando essas informações para controlar posteriormente a saída.

---

# 2. Requisitos Funcionais

## RF01 – Identificação por RFID

Ao aproximar uma tag RFID do leitor, o sistema deverá verificar se seu identificador está presente na lista de usuários autorizados.

Caso a tag seja válida, o processo de autenticação deverá continuar.

Caso a tag não esteja cadastrada, a entrada deverá ser recusada.

---

## RF02 – Cadastro da Tag

O sistema deve ser capaz de cadastrar novas tags e descadastrar tags.

---

## RF03 – Identificação do Período do Dia

O sistema deverá identificar se o acesso está ocorrendo durante o período diurno ou noturno.

A identificação deverá ser realizada prioritariamente utilizando o horário do sistema.

Opcionalmente, um sensor de luminosidade poderá ser utilizado como mecanismo alternativo caso a obtenção do horário não esteja disponível.

---

## RF04 – Autenticação Diurna

Durante o período definido como diurno, uma tag RFID válida deverá ser suficiente para autorizar a entrada do veículo.

Fluxo esperado:

`Tag RFID → validação → autorização → abertura da cancela`

---

## RF05 – Autenticação Noturna

Durante o período definido como noturno, o sistema deverá exigir dois fatores de autenticação:

1. Tag RFID válida;
2. Senha correta inserida por meio de um teclado matricial.

Fluxo esperado:

`Tag RFID → validação → solicitação de senha → validação da senha → abertura da cancela`

A cancela somente deverá ser aberta quando as duas etapas forem concluídas corretamente.

---

## RF06 – Controle da Cancela

O sistema deverá controlar a abertura e o fechamento de uma cancela utilizando um servomotor.

Após a autenticação do usuário, o servo deverá movimentar a cancela da posição fechada para a posição aberta.

---

## RF07 – Detecção da Passagem do Veículo

Um sensor ultrassônico deverá ser utilizado para detectar a presença e a passagem do veículo pela região da cancela.

Enquanto um veículo estiver sendo detectado na área de passagem, a cancela deverá permanecer aberta.

---

## RF08 – Fechamento Automático da Cancela

Após detectar que o veículo passou completamente pela cancela, o sistema deverá comandar o servomotor para retornar a cancela à posição fechada.

O fechamento não deverá ocorrer enquanto o sensor indicar a presença de um veículo na região da cancela.

---

## RF09 – Registro de Entrada

Após uma entrada bem-sucedida, o sistema deverá registrar que o veículo correspondente à tag RFID entrou no estacionamento.

O registro deverá armazenar, no mínimo:

* identificação da tag;
* identificação do veículo ou usuário;
* horário de entrada;
* estado atual do veículo no estacionamento.

---

## RF10 – Controle dos Veículos Presentes

O sistema deverá manter uma relação dos veículos que se encontram atualmente dentro do estacionamento.

Esse controle será utilizado para verificar se um determinado veículo possui autorização para realizar a saída.

---

## RF11 – Autorização de Saída

Para realizar a saída, o veículo deverá novamente ser identificado pelo RFID.

A saída somente deverá ser autorizada caso o veículo esteja registrado como presente no estacionamento.

Após sua saída, o sistema deverá atualizar seu estado para indicar que ele não está mais dentro do estacionamento.

---

## RF12 – Prevenção de Entradas Duplicadas

Caso uma tag associada a um veículo que já esteja registrado dentro do estacionamento tente realizar uma nova entrada, o sistema deverá rejeitar ou sinalizar a operação.

---

## RF13 – Tratamento de Tag Inválida

Caso uma tag RFID não cadastrada seja apresentada, o sistema deverá:

* negar o acesso;
* manter a cancela fechada;
* informar que o acesso não foi autorizado.

---

## RF14 – Tratamento de Senha Incorreta

Durante o período noturno, caso a senha informada seja incorreta, o sistema deverá negar o acesso e manter a cancela fechada.

O sistema poderá limitar a quantidade de tentativas consecutivas de senha.

---

## RF15 – Tratamento de Falha no Sensor Ultrassônico

O sistema deverá soar um alarme com o buzzer e lentamente fechar a cancela caso o sensor responsável pela detecção da passagem apresente valores inválidos ou deixe de responder.

O sistema deverá sinalizar a falha e poderá exigir intervenção manual para retornar à operação normal.

---

## RF16 – Tratamento de Falha no RFID

Caso o leitor RFID deixe de responder ou apresente erro de leitura, o sistema deverá manter a cancela fechada e impedir uma autorização automática de entrada.

---

## RF17 – Sinalização Sonora

Opcionalmente, um buzzer poderá ser utilizado para fornecer sinais sonoros diferentes para situações como:

* acesso autorizado;
* acesso negado;
* senha incorreta;
* erro do sistema;
* abertura da cancela.

---

## RF18 – Interface com Display - opcional

Opcionalmente, um display LCD poderá apresentar informações ao usuário durante o processo de autenticação.

Exemplos:

* `Aproxime a tag`
* `Tag reconhecida`
* `Digite a senha`
* `Acesso autorizado`
* `Acesso negado`
* `Cancela aberta`
* `Aguarde`
* `Erro no sensor`

---

# 3. Requisitos Não Funcionais

## RNF01 – Segurança

A cancela deverá permanecer fechada por padrão.

Falhas de leitura, autenticação ou comunicação com os sensores não deverão resultar automaticamente na abertura da cancela.

---

## RNF02 – Segurança Física

O sistema deverá evitar o fechamento da cancela enquanto houver um veículo detectado em sua área de passagem.

---

## RNF03 – Tempo de Resposta

O sistema deverá realizar a validação da tag RFID e fornecer uma resposta ao usuário em poucos segundos, evitando atrasos significativos no processo de entrada.

---

## RNF04 – Modularidade

O software deverá ser organizado de forma modular, permitindo o desenvolvimento e teste independente dos principais componentes:

* RFID;
* teclado matricial;
* servomotor;
* sensor ultrassônico;
* controle de horário;
* buzzer;
* LCD;
* sistema de registro.

---

## RNF05 – Manutenibilidade

O código deverá possuir organização e nomenclatura que facilitem futuras alterações, como cadastro de novos usuários, mudança dos horários de funcionamento ou inclusão de novos sensores.

---

## RNF06 – Tolerância a Falhas

Falhas em periféricos não deverão provocar comportamentos potencialmente perigosos.

Sempre que não for possível determinar com segurança o estado do sistema, deverá ser adotado um estado seguro.

---

# 4. Periféricos Previstos

| Periférico             | Função                                        |
| ---------------------- | --------------------------------------------- |
| Leitor RFID RC522      | Identificação dos veículos                    |
| Tags RFID              | Credenciais de identificação                  |
| Servomotor             | Simulação da abertura e fechamento da cancela |
| Sensor ultrassônico    | Detecção da passagem do veículo               |
| Teclado matricial      | Digitação da senha durante o período noturno  |
| Buzzer                 | Sinalização sonora de eventos                 |
| Display LCD (opcional) | Exibição de mensagens ao usuário              |
| Sensor de luminosidade | Identificação alternativa de dia/noite        |

Os dois últimos componentes podem ser tratados como extensões do projeto caso haja tempo disponível para sua implementação.

---

# 5. Fluxo Principal de Entrada

### Entrada durante o dia

`Veículo se aproxima`

↓

`Usuário aproxima a tag RFID`

↓

`Sistema identifica a tag`

↓

`Tag cadastrada?`

**Não → Acesso negado**

**Sim → Acesso autorizado**

↓

`Servomotor abre a cancela`

↓

`Veículo atravessa`

↓

`Sensor ultrassônico detecta a passagem`

↓

`Área da cancela fica livre`

↓

`Cancela fecha`

↓

`Veículo é registrado como presente no estacionamento`

---

# 6. Fluxo Principal de Entrada Noturna

`Veículo se aproxima`

↓

`Usuário aproxima a tag RFID`

↓

`Tag válida?`

**Não → Acesso negado**

**Sim → Solicitar senha**

↓

`Usuário digita senha`

↓

`Senha correta?`

**Não → Acesso negado**

**Sim → Acesso autorizado**

↓

`Cancela abre`

↓

`Veículo passa`

↓

`Sensor detecta que a área ficou livre`

↓

`Cancela fecha`

↓

`Entrada registrada`

---

# 7. Fluxo Principal de Saída

`Veículo solicita saída`

↓

`Tag RFID é identificada`

↓

`Veículo está registrado no estacionamento?`

**Não → Saída não autorizada / erro de registro**

**Sim → Saída autorizada**

↓

`Cancela abre`

↓

`Veículo passa`

↓

`Sensor detecta passagem`

↓

`Cancela fecha`

↓

`Veículo é removido da lista de veículos presentes`

---

# 8. Escopo Inicial

Para a primeira versão funcional do projeto, serão considerados componentes essenciais:

1. leitura da tag RFID;
2. cadastro e validação de usuários;
3. controle de horário;
4. autenticação por senha no período noturno;
5. controle do servomotor;
6. leitura do sensor ultrassônico;
7. controle dos veículos presentes no estacionamento;
8. tratamento dos principais casos de falha.


# 9. Objetivo da Primeira Etapa

Nesta etapa inicial, o projeto deverá estabelecer claramente o comportamento esperado do sistema e sua arquitetura antes da integração completa dos componentes.

A implementação deverá ser realizada de forma incremental, inicialmente testando individualmente RFID, teclado, servomotor e sensor ultrassônico e, posteriormente, realizando a integração dos módulos no sistema completo de controle de acesso.


# 10. Licença

Copyright (C) 2026 caioma

Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License, versão 3, conforme publicada pela Free Software Foundation.

Este programa é distribuído na expectativa de que seja útil, mas SEM NENHUMA GARANTIA; sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO FIM. Consulte a GNU General Public License para mais detalhes.

O texto completo da licença está disponível no arquivo [LICENSE](LICENSE).
