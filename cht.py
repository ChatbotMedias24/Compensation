import streamlit as st
import openai
import streamlit as st
from dotenv import load_dotenv
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import os
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from streamlit_chat import message  # Importez la fonction message
import toml
import docx2txt
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
import docx2txt
from dotenv import load_dotenv
if 'previous_question' not in st.session_state:
    st.session_state.previous_question = []

# Chargement de l'API Key depuis les variables d'environnement
load_dotenv(st.secrets["OPENAI_API_KEY"])

# Configuration de l'historique de la conversation
if 'previous_questions' not in st.session_state:
    st.session_state.previous_questions = []

st.markdown(
    """
    <style>

        .user-message {
            text-align: left;
            background-color: #E8F0FF;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: 10px;
            margin-right: -40px;
            color:black;
        }

        .assistant-message {
            text-align: left;
            background-color: #F0F0F0;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: -10px;
            margin-right: 10px;
            color:black;
        }

        .message-container {
            display: flex;
            align-items: center;
        }

        .message-avatar {
            font-size: 25px;
            margin-right: 20px;
            flex-shrink: 0; /* Empêcher l'avatar de rétrécir */
            display: inline-block;
            vertical-align: middle;
        }

        .message-content {
            flex-grow: 1; /* Permettre au message de prendre tout l'espace disponible */
            display: inline-block; /* Ajout de cette propriété */
}
        .message-container.user {
            justify-content: flex-end; /* Aligner à gauche pour l'utilisateur */
        }

        .message-container.assistant {
            justify-content: flex-start; /* Aligner à droite pour l'assistant */
        }
        input[type="text"] {
            background-color: #E0E0E0;
        }

        /* Style for placeholder text with bold font */
        input::placeholder {
            color: #555555; /* Gris foncé */
            font-weight: bold; /* Mettre en gras */
        }

        /* Ajouter de l'espace en blanc sous le champ de saisie */
        .input-space {
            height: 20px;
            background-color: white;
        }
    
    </style>
    """,
    unsafe_allow_html=True
)
# Sidebar contents
textcontainer = st.container()
with textcontainer:
    logo_path = "medi.png"
    logoo_path = "NOTEPRESENTATION.png"
    st.sidebar.image(logo_path,width=150)
   
    
st.sidebar.subheader("Suggestions:")
questions = [
        "Donnez-moi un résumé du rapport ",
        "Comment l'évolution des prix mondiaux du pétrole et du gaz butane affectera-t-elle la charge de compensation en 2025 ?",
        "Comment le contexte économique international pourrait-il influencer la politique de compensation pour l'année 2025 ?",
        "Comment les dépenses de compensation au Maroc se comparent-elles à celles d’autres pays similaires ?" ]

# Initialisation de l'historique de la conversation dans `st.session_state`
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = StreamlitChatMessageHistory()
def main():
    text="""
    
INTRODUCTION

Le marché mondial des matières premières de base continue de subir, globalement, en 2024,
une forte volatilité dans le sillage de la persistance des défis géopolitiques, économiques,
logistiques et climatiques. En dépit du recul de l’inflation, et les perspectives d’'un
assouplissement monétaire, les cours mondiaux des produits énergétiques et alimentaires se
sont montrés plus résistants, en se limitant à une légère baisse par rapport aux niveaux
enregistrés en 2023, et en restant largement en dessus des niveaux conventionnels
enregistrés avant la succession des crises depuis l’année 2021.

Ainsi, le cours du pétrole brut Brent a oscillé, au titre de la période allant de janvier à août
2024, dans une fourchette comprise entre 75,9 $/bbl et 91,2 $/bbl, avec une moyenne de
82,9 $/bbl, soit une hausse de 3 % en glissement annuel. En ce qui concerne le gaz butane,
son cours suivant la formule marocaine a fluctué, au titre de la même période, entre un
minimum de 445 $/T et un maximum de 601 $/T, soit une moyenne de 537 $/T, enregistrant
un léger repli de 0,7 % en glissement annuel

Ces niveaux de cours, presque comparables à ceux de l'année 2023, résultent des
conséquences de l'embargo sur le pétrole russe et d'une politique de l'offre marquée par une
intervention accrue de l'OPEP+ en vue de réguler les prix. Aussi, les tensions géopolitiques
au Moyen-Orient et le recul des stocks mondiaux du produit ont également accentué la
tendance haussière du marché du Brent durant une grande partie de l'année 2024.
Néanmoins, l'affaiblissement de la demande de pétrole dans les principales économies
mondiales a entraîné une chute du prix de ce produit, qui a fluctué entre 69,1 $/bbl et
73,7 $/bbl au titre de la première quinzaine du mois de septembre 2024.

S'agissant du marché du gaz butane, il a été considérablement impacté par la forte volatilité
du marché pétrolier. En effet, |le commerce mondial de ces deux produits et leurs cours ont
été affectés par les crises survenues au niveau des canaux de Suez et de Panama, considérés
comme les deux principaux passages maritimes intercontinentaux d’échanges mondiaux. Le
canal de Suez a subi les répercussions des tensions géopolitiques régionales, tandis que le
canal de Panama a observé une baisse importante de son niveau en raison du phénomène
météorologique El Niño.

Par rapport aux produits pétroliers liquides, leurs cours ont affiché des corrélations négatives
avec ceux du pétrole brut. Les cours du gasoil et du super ont enregistré, au titre des huit
premiers mois de l'année 2024, des baisses en glissement annuel de 18 % et 44 %
respectivement, portant leurs moyennes pour ladite période à 800 $/T et 884 $/T.

Concernant les cours mondiaux des produits alimentaires subventionnés, ils se sont repliés
durant la période allant de janvier à août 2024 tout en enregistrant une instabilité prononcée.
La baisse la plus marquée a été observée sur le marché du blé tendre, dont le prix s'est
contracté de plus de 16 % par rapport à la même période de l’année précédente, en
atteignant un niveau moyen de 233 $/T. Cette situation s'explique par une augmentation
significative de l'offre, résultant de récoltes abondantes en Amérique du Nord, en Europe et
en Asie, ainsi que par la continuité des exportations ukrainiennes de blé tendre dans le cadre
de l'Initiative de la mer Noire, supervisée par l'ONU.

Pour le sucre brut, après avoir atteint des sommets pluriannuels en 2023, ses cours ont
enregistré une baisse de 12 % en glissement annuel sur la période de janvier à août 2024,
s'établissant à une moyenne de 483 $/T. Cette baisse des prix résulte d'une amélioration
significative de la production brésilienne, malgré la poursuite par l'Inde de sa politique de
restriction d'exportation pour la deuxième année consécutive, visant à soutenir le marché
local face aux perspectives de baisse de la production de la canne à sucre.

En somme, les premiers mois de l'année 2024 ont été caractérisés par la persistance de la
montée des cours des produits subventionnés sur le marché international, d’une part, et par



les conditions de sécheresse de la campagne agricole 2023/2024 au niveau national, qui ont
impacté considérablement le niveau de la production locale en sucre et en blé tendre,
d’autre part. De ce fait, afin de contenir l’inflation et assurer un approvisionnement régulier
du pays en produits de base, et permettre la stabilisation des prix intérieurs dans l’objectif du
soutien du pouvoir d’achat des citoyens, le Gouvernement a pris plusieurs mesures.

Pour la bonbonne du gaz butane de 12 kg, malgré l'augmentation de son prix de vente de
10 DH à partir du 20 mai 2024, la subvention octroyée par l’Etat pour le soutien de son prix à
la consommation, demeure importante en s'élevant en moyenne à 63 DH au titre de la
période janvier-août 2024, en baisse de 9% par rapport à la même période de l’année
précédente. De ce fait, la charge de compensation du gaz butane, s’élève au titre de ladite
période, à près de 10,45 milliards de dirnams.

S'agissant du sucre, afin de maintenir le prix de vente inchangé sur le marché national,
malgré la récente revalorisation des prix d’achat des cultures sucrières, effective depuis le
14 avril 2023, et dans le but d’encourager les agriculteurs à relancer la production nationale
de sucre blanc, la subvention forfaitaire accordée par l’État à la consommation du sucre a été
réévaluée à la hausse de 27 %, atteignant ainsi 3,6 DH/kg. Par conséquent, la charge de
subvention à la consommation de sucre raffiné s’est élevée, pour la période de janvier à août
2024, à 3,08 milliards de dirhams, enregistrant une hausse d’environ 15 % en glissement
annuel.

Quant au sucre brut, et afin de compenser le déficit croissant de la production nationale de
sucre blanc, résultant des conditions de sécheresse, dans un contexte international
caractérisé par des niveaux élevés des cours du sucre brut, l’État a octroyé une subvention
additionnelle moyenne pondérée à l'importation de ce produit, de 2,18 DH/kg pour |la période
de janvier à août 2024. Ainsi, la charge liée à l'importation du sucre brut durant cette période
s'est élevée à 1,35 milliard de dirnams, marquant une augmentation de 10 % par rapport à la
même période de l'année précédente

En conséquence, la charge globale relative au soutien du sucre (sucres raffiné et brut) a
atteint un montant de 4,43 milliards de dirnams au titre de ladite période, en progression de
13,36% par rapport à la même période de l’année précédente.

Concernant la farine nationale du blé tendre, le Gouvernement a maintenu la subvention
unitaire de 143,375 DH/quintal pour le même niveau de contingent de farine nationale de blé
tendre, soit 6,26 millions de quintaux. Cela a engendré une charge budgétaire de près de
880 millions de dirnams pour la période allant de janvier à août 2024, incluant les actions
menées pour la valorisation de la production locale de blé tendre, notamment la prise en
charge des frais de stockage et de magasinage.

Pour le blé tendre, au vu du déficit de la production nationale de ce produit au titre de la
campagne agricole 2023/2024 suite aux effets de la sécheresse et à la poursuite du
dépassement du prix de revient à l'importation du blé tendre au prix cible, l'Etat a maintenu,
en sus de la suspension des droits de douane à l’importation durant l’année 2024, l’octroi
d'une subvention à l'importation du blé tendre. La finalité étant de sécuriser
l’approvisionnement du marché national en cette denrée et stabiliser le prix du pain à
1,20 DH et les prix des farines.

De ce fait, la prime forfaitaire octroyée par l’Etat à l'importation du blé tendre a enregistré,
au titre de la période janvier-août 2024, une moyenne de 13,17 DH/Quintal contre
62,15 DH/Quintal au titre de la même période en 2023, en déclin de 79%. Ainsi, le soutien à
l'importation du blé tendre, s’est élevé à 687 MDH à fin août 2024, en recul de 69% par

rapport à la même période de l’année 2023.



RAPPORT SUR LA COMPENSATION

Par conséquent, la charge globale relative au soutien du blé importé et de la farine nationale
du blé tendre a atteint un montant de 1,57 milliard de dirnams au titre de ladite période, en
recul de 50 % en glissement annuel

Aussi, l’Etat poursuit le soutien de prix à la consommation de certains produits alimentaires
en faveur des populations des provinces du sud pour un montant de 88 MDH au titre de la
période janvier-août de l’année 2024 ;

En ce qui concerne les carburants, et dans le cadre de la poursuite de sa politique de lutte
contre l'inflation, notamment par la stabilisation des tarifs de transport des personnes et des
marchandises, l'État a maintenu, pour l'année 2024, le soutien exceptionnel accordé aux
transporteurs routiers. Le montant alloué à cette opération pour la période allant de janvier à
août 2024 s'élève à 1,55 milliards de dirhams, contre 800 MDH pour la même période de
l'année précédente.

Par ailleurs, l'Etat continuerait de soutenir les prix du gaz butane, du sucre et de la farine
nationale du blé tendre, à travers la programmation d’une enveloppe de 16,536 milliards de
dirhams au titre du projet de la loi de finances 2025.



CHAPITRE I : EVOLUTION DU MARCHE
INTERNATIONAL DES PRODUITS SUBVENTIONNES

1.1. Marché pétrolier

Le marché du pétrole brut a été caractérisé par une forte volatilité des prix, durant les deux
dernières années, sous l'infuence de multiples facteurs macroéconomiques et
géopolitiques. Cette volatilité est principalement due aux réductions de la production de
l'OPEP+ qui ont maintenu l'offre en dessous de la demande, conduisant à une diminution
des stocks mondiaux. Par ailleurs, la demande mondiale de pétrole a été stimulée par la
consommation américaine, mais freinée par la faiblesse économique en Chine et en Europe.

1.1.1. Commerce international du pétrole
1.1.1.1. Demande mondiale de pétrole

En 2023, la demande mondiale de pétrole a atteint 101,7 millions de barils par jour (b/j), soit,
globalement, une hausse de 2 millions de b/j par rapport à l’année 2022. Ce développement
est dû à la reprise de l’activité économique en chine, notamment dans le secteur
pétrochimique, et à une augmentation globale des voyages en avion après la pandémie. La
consommation a culminé vers la fin de l’année, en atteignant environ 102,5 millions de b/j au
second semestre.

Dans les pays de l’'OCDE, la demande de pétrole était de 45,76 millions (b/j) en 2023,
marquant une stagnation relative par rapport à 2022. Cette stabilité de la demande est
principalement expliquée par une augmentation de la demande dans les Etats-Unis
(+220 kb/j), compensée en grande partie par des baisses en Europe (-140 kb/j) et en
Pacifique (-10 kb/j). Cette évolution est attribuable à la résilience de l'économie américaine,
tandis que l'Europe a souffert d'un affaiblissement de l'activité industrielle et d'une
stagnation économique.

Concernant les pays non OCDE, la demande a augmenté à 55,97 millions (b/j), marquant
une hausse de 2,2 millions b/j par rapport à 2022. La Chine a représenté une part
significative de cette augmentation, avec une demande moyenne atteignant un niveau de
16,4 millions (b/j). La demande chinoise a été stimulée par plusieurs facteurs, notamment la
reprise économique après les restrictions liées à la pandémie, une forte croissance du
secteur pétrochimique, ainsi qu'une augmentation de la mobilité et du transport. La reprise
économique dans d'autres pays non-OCDE a également contribué à cette augmentation,
notamment grâce à une expansion dans les secteurs du transport et de l'industrie.

Au titre du premier trimestre de l’année 2024, La croissance de la demande mondiale de
pétrole a continué de ralentir, avec une augmentation limitée à 1,6 millions (b/j) en
glissement annuel. Cette diminution est attribpuée à des livraisons exceptionnellement
faibles dans les pays de l'OCDE à cause d’un hiver exceptionnellement chaud qui a réduit
l'utilisation de combustibles de chauffage et de fuel pour la production de l’électricité.

Au deuxième trimestre de l'année 2024, la croissance de la demande mondiale de pétrole a
poursuivi son ralentissement, s'établissant à 710 Kb/j en glissement annuel, ce qui constitue
la plus faible hausse trimestrielle depuis le quatrième trimestre de 2022. Cette évolution
s'explique principalement par la baisse de la consommation en Chine, longtemps perçue
comme le moteur essentiel de la croissance de la demande mondiale de pétrole, en raison
d'une contraction de la demande en carburants industriels et en matières premières
pétrochimiques.

La décélération continue de la croissance de la demande au troisième trimestre laisse

S



RAPPORT SUR LA COMPENSATION

présager une augmentation de la demande mondiale de pétrole de l'ordre de 900 Kb/j
pour l'année 2024, contre 2 Mb/j en 2023, selon le dernier rapport publié en septembre par
l'Agence Internationale de l'Énergie. Cette dynamique, selon la même agence, devrait rester
modérée en 2025, avec une croissance estimée à environ 1 million de barils par jour.

1.1.1.2 Offre mondiale de pétrole

En 2023, l'offre mondiale de pétrole a atteint un niveau record de 101,9 millions de barils par
jour (mb/j). Cette augmentation de 18 mb/j par rapport à l'année précédente est
principalement due à une production accrue aux États-Unis, au Brésil, et en Guyane, ainsi
qu'à une hausse des exportations iraniennes. En revanche, les membres de l'OPEP+ ont
réduit leur production de 400 kb/j en raison des coupes volontaires de l'Arabie Saoudite.

L'année 2024 se présente comme une période de transition et de volatilité sur le marché
pétrolier mondial, marquée par des fluctuations dans les stocks mondiaux, des ajustements
de production par l'OPEP+, et des incertitudes économiques qui influencent les prix du
pétrole. La production globale de pétrole montre des signes de croissance, principalement
due aux augmentations de la production non-OPEP+, en particulier aux États-Unis, au
Brésil, en Guyane et au Canada. Cependant, les coupes volontaires de l'OPEP+ et les
tensions géopolitiques continuent de jouer un rôle crucial dans la détermination des prix et
de la disponibilité du pétrole sur les marchés mondiaux.

Au premier trimestre, les stocks mondiaux ont augmenté significativement, reflétant des
tensions sur les routes maritimes qui ont poussé les stocks "sur l'eau” à des niveaux record.
Pour le deuxième trimestre, L'offre mondiale a augmenté sous l'impulsion des producteurs
non-OPEP+, mais la demande chinoise a montré des signes de faiblesse, influençant
négativement les projections de croissance de la demande globale. Malgré une
augmentation continue des stocks jusqu'au mois de mai, une baisse a été observée en juin,
indiquant une volatilité persistante dans la gestion des stocks

Au titre du mois de juillet, une légère augmentation de l'offre mondiale a été observée, avec
une production accrue de l'OPEP+ qui a plus que compensé les baisses chez les
producteurs non-OPEP+. Pour le reste de l’année, il est prévu que la production continue
sur une trajectoire de croissance positive, particulièrement parmi les producteurs non-
OPEP+. Cependant, l'OPEP+ pourrait ajuster ses niveaux de production en fonction des
conditions du marché, ce qui pourrait influencer les prix et la disponibilité du pétrole dans
les mois à venir.

Evolution de l'offre et de la demande mondiales du pétrole (Mbbl/j)

103,09

101,98

101,29 101,43

2023 T1-2024 T2-2024

mDemande » Offre

Source : Agence Internationale de l’Energie et l’'Administration américaine de l’information sur l’'Energie (ElA)

La production de pétrole aux États-Unis a atteint des niveaux record en 2023 et devrait
continuer à croître en 2024. En 2023, la production a augmenté, atteignant un pic de
12,9 millions de barils par jour. Cette hausse est due en partie à une plus grande efficacité

N



l PROJET DE LOI DE FINANCES POUR L'ANNEE 2025 l

dans l'utilisation des équipements de forage malgré une baisse du nombre de ces derniers
en activité. Les projections pour 2024 indiquent que la production pourrait atteindre une
moyenne de 13,24 millions de barils par jour, et même approcher les 13,5 millions de barils
par jour vers la fin de l'année.

Evolution trimestrielle de la production américaine du pétrole (Mbbl/j)

13,26 13,21
13,07
12,94
12,75
n '
T1-23 T2-23 T3-23 T4-23 T1-24 T2-24

Source : Administration Américaine de l’Information sur l'Energie.

Après avoir enregistré une accumulation durant les premiers mois de 2024, les réserves
mondiales ont commencé à baisser à partir du mois de juin. En effet, les réserves ont
augmenté de 23,9 millions de barils en mai, mais ont baissé de 18,1 millions de barils en juin.

Selon l’Agence Internationale de l’énergie, il est prévu que les stocks mondiaux de pétrole
continuent de diminuer en raison des coupes de production de l'OPEP+. Cette diminution
sera importante surtout dans la seconde moitié de 2024, avec des baisses moyennes de
0,8 million de barils par jour. Toutefois, les stocks pourraient augmenter à nouveau d’une
façon modérée à partir du 2°"° semestre de l’année 2025 après l'expiration des coupes
volontaires de l'OPEP+, avec des augmentations moyennes de 0,3 million de barils par jour.

1.1.1.3 Echanges mondiaux de pétrole

En 2023, les échanges mondiaux de pétrole ont connu des changements importants en
raison des facteurs géopolitiques et économiques. La réorientation des flux pétroliers
mondiaux a été marquée par la réorganisation des exportations russes, passant de l'Europe
à l'Asie, tandis que l'Europe a intensifié ses importations en provenance des États-Unis et
d'autres régions.

Evolution des exportations des
principaux fournisseurs mondiaux du
pétrole (MT)

443
4152 3338 L09,9
384,5
i
Etats-Unis Arabie Saoudite Russie
m2022 52023

Evolution des importations des
principaux clients mondiaux du
pétrole (MT)

6783

695
sm 600,9
m13 4213
l 2843 285

Europe Chine Etats-Unis Inde
= 2022 # 2023

Source : BP Statistical World Energy 2023

N



RAPPORT SUR COMPENSATION

En 2023, les importations de pétrole aux États-Unis ont emprunté deux tendances
distinctes. De janvier à août, elles ont affiché une augmentation, passant de 8,42 millions de
barils par jour (mb/j) à 8,93 mb/j. Cependant, cette tendance s'est inversée durant le reste
de l'année, pour rechuter à 8,46 mb/j en décembre. Au cours du premier semestre de 2024,
les importations mensuelles moyennes se sont élevées à 259,42 millions de barils, reflétant
ainsi une relative stabilité par rapport à la même période de l'année précédente. Malgré sa
position de premier producteur mondial, les États-Unis ont exporté environ 3,6 millions de
barils par jour de pétrole brut, principalement vers l'Europe et les pays voisins comme le
Mexique et le Canada.

L’Arabie Saoudite a maintenu sa position comme le premier exportateur de pétrole.
Cependant, la production a légèrement diminué par rapport aux années précédentes en
raison des efforts de l'OPEP+ pour stabiliser les prix via des réductions de production.

La Russie a continué d'exporter d'importantes quantités de pétrole, mais les sanctions
imposées à la suite du conflit avec l’'Ukraine ont redirigé une partie de ses flux vers l'Asie
(notamment la Chine et l'Inde). Les exportations ont chuté en Europe mais ont été
partiellement compensées par des accords bilatéraux avec les pays asiatiques.

En 2023, la Chine, premier importateur mondial de pétrole brut, a accru ses achats à
11,3 millions de barils par jour, marquant une augmentation de 10 % par rapport à 2022. Les
raffineries du pays ont atteint des niveaux record d'importations afin de soutenir
l’expansion de leur capacité de traitement, répondant ainsi à la demande croissante en
carburant pour le secteur des transports et fournissant des matières premières essentielles
à une industrie pétrochimique en pleine expansion.

En 2024, les exportations de pétrole des pays non membres de l'OPEP (États-Unis, Brésil,
Canada, Guyana) continuent de croître, avec une augmentation de 1,2 mb/j, malgré les
réductions de production des pays de l'OPEP+ visant à soutenir les prix mondiaux. Les
États-Unis devraient atteindre un record historique, dépassant les 13 mb/j d'exportations de
pétrole. Bien que l'Arabie saoudite et la Russie restent des acteurs clés sur le marché
mondial, leur part dans les exportations diminue en raison de leur politique volontaire de
réduction de production pour stabiliser les marchés pétroliers.

La Chine connaît un net ralentissement de ses importations de pétrole, avec une
augmentation de seulement 620 kb/j en 2024, contre 1,7 mb/j en 2023. Ce ralentissement
s'explique par la transition vers les véhicules électriques et une croissance économique plus
modérée. En revanche, l'Inde continue d'accroître ses importations pour répondre à une
demande intérieure en pleine expansion. La demande des pays non membres de l'OCDE
poursuit sa croissance, compensant en partie la baisse de la demande dans les pays de
l'OCDE.

La crise de la mer Rouge en 2024 a gravement perturbé les échanges mondiaux de pétrole,
causant des retards et une hausse des coûts de transport. Les attaques observées contre
les navires pétroliers, ont poussé les acteurs à contourner l'Afrique, rallongeant les trajets et
réduisant temporairement l'offre de pétrole. Cette situation a impacté les exportations des
pays du Golfe et augmenté les coûts liés au transport maritime.

Pour les pays importateurs, en particulier en Europe et en Asie, la crise de la mer Rouge a
engendré des tensions sur les stocks de pétrole, obligeant certains à puiser dans leurs
réserves stratégiques. D'autres ont cherché des sources alternatives à court terme pour
compenser les retards. Certains importateurs asiatiques ont aussi diversifié leurs
approvisionnements, en augmentant les importations en provenance des États-Unis, du
Brésil et du Canada afin de réduire leur dépendance aux flux traversant la mer Rouge.



1.1.2. Evolution des cours mondiaux des produits pétroliers
1.1.2.1. Evolution des cours du pétrole brut

» Evolution des prix en 2023

En 2023, le prix moyen annuel du pétrole brut Brent s’est établi à 82 $/baril, contre
99 $/baril en 2022, enregistrant ainsi une baisse de près de 17 %. Cette diminution résulte
de plusieurs facteurs, dont la réorientation des exportations russes vers des marchés hors
de l'Union européenne, les ajustements de la demande mondiale de pétrole, ainsi que les
réductions de production décidées par l'OPEP+.

Depuis le dernier trimestre de l’'année 2022, les prix moyens du Brent n’ont pas réussi à
dépasser le seuil des 90 $/baril. Au premier trimestre 2023, le cours moyen du Brent s'est
maintenu autour de 82 $/bbl, soutenu par les ajustements des exportations mondiales de
pétrole, en grande partie liés aux sanctions contre la Russie. Par la suite, une offre
excédentaire de certains producteurs hors OPEP+ a fait légèrement fléchir les prix à une
moyenne de 78 $/bbl au deuxième trimestre. Cependant, au troisième trimestre, le Brent a
rebondi, atteignant une moyenne d'environ 86 $/bbl, stimulé par les réductions de
production de l'OPEP+ et l'augmentation de la demande mondiale.

N

Evolution des moyennes trimestrielles
du cours du Brent ($/bbl)

8683 87
72 71
64
51 55
44 43
S S D A 0 0P Û » »
â@*n”°”%”°”°”°“'%”%”e”@” S C R E S
OE SE E SE E E SSF SSSSS SS $

Evolution annuelle du cours du
Brent ($/bbl)

105

97 99

Source : Bloomberg

Au cours du dernier trimestre de 2023, les prix du Brent ont suivi une tendance à la baisse,

passant de 85 $/baril au début du trimestre à
atteint un pic de 92 $/baril. Cette baisse des
facteurs, dont l'augmentation de l’offre de pétro

78 $/baril en fin de période, après avoir
cours s'explique par une combinaison de
le provenant des États-Unis, du Brésil et de

l'Iran, ainsi que par un ralentissement de la demande mondiale, particulièrement en Chine et
en Europe.

» Evolution des prix en 2024

Entre janvier et août 2024, le prix du baril de Brent a fluctué dans une fourchette comprise
entre 76 $/bbl et 91 $/bbl, atteignant une moyenne de 83 $/bbl, soit une augmentation de
près de 3 % par rapport à la même période en 2023.

En janvier 2024, le Brent a enregistré un prix moyen de 79 $/bbl, un niveau relativement

bas principalement attribué à une augmentation de l'offre en provenance de pays non
membres de l'OPEP+, tels que les États-Unis et le Brésil, compensant ainsi les réductions de

N



RAPPORT SUR LA COMPENSATION

production appliquées par l'OPEP+.

Durant les mois de février, mars et avril 2024, les cours de Brent ont connu des
augmentations consécutives passant de 82 S$/bbl à 89 S$/bbl. Ces hausses sont
principalement expliquées par une baisse des stocks mondiaux de pétrole, notamment dans
les pays non membres de l'OCDE, et d'une augmentation saisonnière de la demande, ainsi
que des perturbations dans la chaîne d'approvisionnement, qui ont limité l'offre.

La tendance s'est inversée à partir du mois de mai 2024. Le cours du Brent a atteint une
moyenne de 82,1 $/bbl au titre de la période mai-août 2024 avec un pic de 83,8 $/bbl en
juillet. Cette baisse s'explique principalement par un afflux croissant de pétrole provenant
des pays hors OPEP+, ainsi qu'une demande modérée en Europe et en Asie, résultant de la
conjoncture économique mondiale. L'offre accrue des États-Unis a contribué à maintenir un
équilibre face à cette demande atone. La légère hausse observée en juillet a été motivée
par des incertitudes liées à la baisse des stocks mondiaux et par des interruptions
temporaires dans les chaînes d’approvisionnement.

N
Evolution mensuelle du cours moyen du Brent en 2024 ($/bbl)
89,00
84,67
83,00 83,00 p
81,72
l l l l l I
jan-24 fév.-24 mar.-24 avr.-24 mai-24 jui-24 juil.-24 août-24 J

Source : Bloomberg

1.1.2.2. Evolution des cours des produits pétroliers liquides

Entre janvier et août 2024, le marché des produits pétroliers liquides a connu une baisse
des prix, notamment pour l’essence et le gasoil, malgré une offre mondiale relativement
stable, soutenue par l'augmentation de la production des pays non membres de l'OPEP, tels
que les États-Unis et le Brésil. Les réductions de production de l'OPEP+ ont exercé une
pression modérée sur l'offre, mais la demande mondiale, bien qu'en hausse, a été freinée
par la faiblesse économique persistante en Chine, limitant ainsi une reprise des prix.

» Evolution du cours du gasoil en 2024

Entre janvier et août 2024, le prix du gasoil a fluctué entre 699 $/T et 921 $/T, avec une
moyenne de 800 $/T, ce qui représente une baisse de 184 % par rapport à la même
période en 2023.

En 2024, le cours du gasoil a traversé des phases de volatilité prononcées. En janvier, il a
suivi une tendance haussière, en passant de 774 $/T au début de l'année pour atteindre
921 $/T en mi-février. Par la suite, entre février et mai, les cours du gasoil ont suivi une nette
tendance à la baisse, atteignant 718 $/T au début du mois de juin. Le cours du gasoil est
ensuite monté à 824 $/T au début du mois de juillet. Cependant, au troisième trimestre de
2024, les prix ont de nouveau chuté, en baissant à 699 $/T à la fin août, marquant ainsi une
baisse de 24 % par rapport au pic enregistré en février.

En début d'année, les prix ont atteint des sommets en raison de la réduction de l'offre liée
aux restrictions de production imposées par l'OPEP+ et à une forte demande, notamment

yN



en Europe. Le faible niveau des réserves a également joué un rôle clé dans la flambée des
prix du gasoil en janvier. Aux États-Unis, les stocks de fuel distillé s'élevaient à 114 millions
de barils à fin novembre 2023, le niveau le plus bas pour cette période de l'année depuis
1951. Les stocks américains de distillats étaient inférieurs de 22 millions de barils (-16%) à la
moyenne saisonnière des dix dernières années. Bien que les réserves se soient améliorées
par la suite, elles restaient encore inférieures de 10 millions de barils (-7%) par rapport à la
moyenne saisonnière vers la fin du mois de janvier.

Cependant, à partir de juillet, les prix ont commencé à baisser. Cette diminution s'explique
par une réduction de la demande saisonnière après la période estivale et par une
stabilisation de l'offre mondiale. De plus, des signes de ralentissement économique dans
certaines régions, notamment en Europe, ont contribué à une baisse de la consommation
de gasoil. Les coûts de fret, qui avaient fortement augmenté en début d'année, ont
également commencé à se stabiliser, aidant ainsi à modérer les prix.

» Evolution du cours de l’essence en 2024

Entre janvier et août 2024, le cours de l’essence a fluctué entre 764 $/T et 1010 $/T,
enregistrant une moyenne de 884 $/T, ce qui représente une baisse de 41 $/T par rapport à
la même période de l'année précédente.

En 2024, les cours de l’essence ont affiché une forte corrélation avec ceux du Brent, une
relation plus marquée que celle observée entre le gasoil et le Brent. Cette tendance reflète
une sensibilité accrue du marché de l’essence aux fluctuations des prix du pétrole brut.

Au début de l'année, les cours du super ont, à l'instar de ceux du Brent, montré une forte
tendance à la hausse. Cependant, au deuxième trimestre, ils ont chuté d’un pic de 1010 $/T
à 829 $/T. Par la suite, les prix sont entrés dans une phase de stabilité relative entre juin et
août.

Evolution des cours moyens mensuels du gasoil et de l'essence en 2024 ($/T)

940 983 901
873 884 857 877
813 824 850 828 ; 767 73 ; 780 722 810
jan.-24 fév.-24 mar.-24 avr.-24 mai-24 jui-24 juil.-24 août-24

MGasoil H Essence

Source : Platts

1.2. Marché du Gaz de Pétrole Liquéfié (GPL)

Le marché mondial du GPL s'est distingué par une stabilité relative au titre de l’année 2024
par rapport aux trois dernières années. Malgré des fondamentaux solides, marqués par la
poursuite de la dynamique de l'offre américaine et l'absorption de la majorité de la
demande provenant de l'Asie, ce marché, essentiellement axé sur l'offre, a été confronté à
plusieurs défis d'approvisionnement. Parmi ces défis figurent les perturbations liées au
Canal de Panama, principal corridor de transmission du produit des États-Unis vers l'Asie,
ainsi que les tensions géopolitiques en Mer Rouge, qui ont temporairement bouleversé de
manière significative les flux commerciaux mondiaux en ce produit. De surcroît, les
conditions climatiques ont perturbé tant l'offre que la demande, exerçant ainsi des

N



RAPPORT SUR LA COMPENSATION

pressions à la fois baissières et haussières sur les prix, tout en modifiant la trajectoire
saisonnière habituelle des cours mondiaux du GPL.

1.2.1. Commerce international du GPL
1.2.1.1. Demande mondiale du GPL

La demande mondiale de GPL a enregistré une hausse de 14,8 MT en 2023 par rapport à
l’année précédente, en atteignant ainsi 357 MT, soit une montée de 4,33 %. L'Asie-Pacifique
demeure la principale région consommatrice, en s'accaparant 47 % de la demande
mondiale. Elle est suivie par l'Amérique du Nord, qui représente 19 % de la consommation
globale. Les autres régions, telles que le Moyen-Orient, la Méditerranée et l'Europe,
présentent des parts similaires, avoisinant les 6 à 7 %. En revanche, l’Afrique ne contribue
qu'à hauteur de 2 % à la consommation mondiale de GPL, mettant en évidence une
disparité significative dans les niveaux de consommation entre les différentes régions du
globe.

En 2023, la demande de GPL a connu des variations significatives selon les régions, révélant
des dynamiques distinctes sur les marchés mondiaux. La Russie et l'Europe de l'Est ont
enregistré la plus forte hausse en termes relatifs, avec une augmentation de 18,17 %, soit
2,79 MT. L'Asie-Pacifique, qui reste le moteur de la croissance de l’utilisation du GPL, a
consolidé sa position avec une augmentation de 8,70 MT, représentant une croissance de
5,47 %. Cette hausse, bien que proportionnellement moins importante que celle observée
en Russie et en Europe de l'Est, demeure la plus élevée en volume. Elle témoigne du rôle
crucial de cette région dans la demande mondiale de GPL, porté par l'industrialisation
rapide, l'urbanisation croissante et une population dense.

En revanche, certaines régions ont affiché des baisses notables de leur consommation de
GPL en 2023. Le Moyen-Orient a enregistré un repli de 1,35 MT, soit une baisse de 4,82 %.
Cette contraction s’explique par une modification des besoins énergétiques locaux et un
moindre recours au GPL dans certains secteurs industriels. De même, l'Europe du Nord-
Ouest a enregistré un repli de 0,49 MT (-2,11 %), attribué à une transition progressive vers
des sources d'énergie alternatives ainsi qu'à une réduction de la demande dans le secteur
pétrochimique, qui reste la locomotive de la consommation dans cette région.

Ces tendances régionales illustrent les disparités dans l'évolution de la consommation de
GPL, dictées par des facteurs économiques, énergétiques et industriels propres à chaque
zone géographique. Les régions en forte croissance, comme l'Asie-Pacifique et l’Afrique,
demeurent les moteurs de la demande mondiale, tandis que d'autres, comme le Moyen-
Orient et l'Europe, semblent amorcer un repli ou une stagnation dans leur utilisation du

GPL.
Evolution de la demande mondiale Poids de la consommation du GPL
du GPL (MT) par région en 2023
Asie Pacifique 547%
Amérique du Nord 19%
Moyen-Orient 7%
Méditerranée |= 7%
Nord-Ouest de l'Europe 6%
Amérique latine 6%
Russie et l'Europe de l'est [== 5%
2019 2020 2021 2022 2023 Mfrique } x
= #

Source :Argus Media et IHS markit



Au cours du premier trimestre 2024, la demande de GPL a évolué de manière contrastée
selon les régions. Aux États-Unis, le vortex polaire de janvier a fortement accru la demande
de chauffage, entraînant une consommation soutenue. En Europe et en Asie, la demande de
chauffage est restée faible en raison de températures plus douces que la moyenne
saisonnière. Cependant, en Europe, la demande pétrochimique a augmenté, principalement
en raison des perturbations des expéditions via la mer Rouge, qui ont poussé les taux
d'exploitation des vapocraqueurs à la hausse. Par ailleurs, le butane a bénéficié d'une
demande accrue pour le mélange d'essence en fin de saison. En Inde, la consommation a
été dynamisée par les subventions gouvernementales dans le cadre du programme PMUY,
qui se sont intensifiées à l'approche des élections générales d'avril-mai 2024, contribuant à
limiter l'accumulation des stocks mondiaux.

En mars, la situation a évolué différemment selon les secteurs. En Europe, la demande de
chauffage est restée modérée, encore affectée par un hiver particulièrement doux.
Toutefois, la demande de GPL dans le secteur pétrochimique a continué de croître,
soutenue par la grande flexibilité des vapocraqueurs européens et une décote marquée du
GPL par rapport au naphta. En Asie, la demande de chauffage est également restée faible,
mais l'Inde a continué de jouer un rôle stabilisateur. Sa consommation accrue, soutenue par
les incitations gouvernementales et les perspectives électorales, a contribué à absorber une
partie de l'excédent d'offre dans la région.

Au cours du deuxième trimestre de l'année, la demande de GPL en Asie a été soutenue par
une augmentation de la consommation des vapocraqueurs, alimentée par des perspectives
de hausse du marché. En Europe, les prix du butane ont chuté en dessous de ceux du gaz
naturel pour la première fois de l'année, notamment en mai et juin, incitant les raffineries ct
les industriels à se tourner vers le butane comme combustible alternatif. Cette baisse des
prix a offert un avantage compétitif pour le butane, particulièrement dans les deux derniers
mois du trimestre. Parallèlement, en Asie, le marché du butane a montré une dynamique
haussière grâce à des approvisionnements stables en provenance du Moyen-Orient et des
États-Unis. Cependant, la demande soutenue de la Chine et de l'Inde a tempéré la baisse
des prix, permettant une certaine stabilité sur le marché asiatique

Durant le troisième trimestre, la demande européenne de GPL a dépassé les attentes,
malgré des températures élevées sur le continent. Le secteur pétrochimique a continué de
bénéficier de l'avantage du GPL par rapport au naphta, consolidant une demande ferme. À
l'échelle mondiale, en dépit de la baisse des prix du brut en fin juillet, les prix des GPL sont
restés soutenus grâce à une forte demande pétrochimique, notamment en Chine. Malgré les
défis économiques croissants dans ce pays, la consommation de GPL a augmenté de
manière significative.

D'après les prévisions les plus récentes, la demande mondiale de GPL devrait atteindre
367,79 millions de tonnes en 2024, représentant une croissance de 3,11 %. Cette dynamique
positive devrait se prolonger en 2025, avec une augmentation prévue de la consommation
mondiale de 9,14 millions de tonnes, portant ainsi le total à 376,93 millions de tonnes.

1.2.1.2. Offre mondiale de GPL

En 2023, la production mondiale de GPL a enregistré une croissance notable de 4,05 % en
glissement annuel, atteignant un volume total de 358 millions de tonnes (MT). Cette
expansion a été principalement portée par l'Amérique du Nord, plus précisément par les
États-Unis, dont la production a augmenté de 7,7 %. La majeure partie de cette
augmentation provient des flux toujours croissants de liquides de gaz naturel issus des
gisements de schiste en amont. Cette progression a permis aux États-Unis de franchir, pour
la première fois, la barre des 105 MT, représentant ainsi plus de 28 % de la production
mondiale. En conséquence, 54 % de la croissance globale de l’offre mondiale est attribuable
aux États-Unis, confirmant leur rôle de moteur essentiel de l’offre dans ce secteur.

L'Asie-Pacifique maintient une position stratégique dans la production mondiale de GPL,

N



RAPPORT SUR COMPENSATION

avec une part de 24 % de l'offre globale, grâce à la concentration importante du secteur de
raffinage, qui reste la principale source de production. De leur côté, la Russie et l'Europe de
l'Est ont enregistré une hausse notable de leur production de 8,8 % en glissement annuel,
représentant ainsi 6 % de l'offre mondiale et contribuant à hauteur de 13 % à la croissance
totale. La Méditerranée, qui compte pour 5 % de la production mondiale, a également
affiché une progression significative de 86 % en glissement annuel, soutenue par
'augmentation de la production en Algérie et le renforcement des capacités des raffineries
régionales, ce qui lui a permis de contribuer à hauteur de 11 % à l'expansion de l'offre
mondiale.

En revanche, certaines régions comme le Moyen-Orient (-0,3 %) et le Nord-Ouest de
’Europe (-3,5 %) ont vu leurs productions se replier, illustrant, respectivement, la politique
de réduction de l'OPEP et des défis énergétiques spécifiques, notamment le recul de la
production des raffineries. Néanmoins, ces régions maintiennent une part significative dans
’offre mondiale, avec des contributions respectives de 20 % et 4 %.

Evolution de l'offre mondiale du GPL Poids de la production du GPL par
(MT) région en 2023
Amérique du Nord 35%
s5 mérique |
Asie Pacifique 24%
>s Moyen-Orient 20%
P 331 Russie et l'Europe de l'est 6%
326
Méditerranée 5%
Nord-Ouest de l'Europe 4%
Amérique latine 4%
Afrique 15 2%
2019 2020 2021 2022 2023

Source : Argus Media et IHS markit

Au cours du premier trimestre 2024, l'offre de GPL aux États-Unis a été fortement impactée
par les conséquences de la tempête hivernale survenue en janvier. Cet événement
climatique a perturbé la production et provoqué une hausse significative de la demande
intérieure, entraînant une chute prononcée des stocks. Cependant, dès le mois de mars, la
situation s'est stabilisée grâce à la reprise progressive de la production et à l'apaisement de
la demande liée au chauffage. Cette stabilisation anticipée a permis d'accroître les
exportations, contribuant à la surabondance du marché mondial et exerçant une pression
baissière sur les prix tout en augmentant la disponibilité de GPL à l'international

Le deuxième trimestre a été caractérisé par une production américaine atteignant des
niveaux historiquement élevés, tandis que la demande demeurait faible. En avril, les
terminaux d'exportation américains approchaient de leur capacité maximale, ce qui a
ralenti, à terme, la croissance de l'offre. Parallèlement, en Europe, les prix du GPL ont été
influencés par une offre excédentaire, exacerbée par la baisse des prix du gaz naturel et la
réduction de la demande de produits pétrochimiques. À la fin de ce trimestre, les
exportations américaines ont été menacées par l'ouragan Beryl, bien que la principale
contrainte reste la capacité limitée des terminaux d'exportation sur la côte du Golfe des
Etats-Unis.

Au troisième trimestre, la concurrence entre l'Europe et l'Asie pour les exportations
américaines de GPL s'est intensifiée. Les prix nets asiatiques, plus élevés que ceux observés

N



en Europe, ont réduit la disponibilité du GPL pour le marché européen. Cette situation a
inversé la dynamique du marché, avec des prix à court terme supérieurs aux valeurs à
terme, et ce, malgré une demande saisonnière relativement faible. En Europe, les niveaux
de stocks élevés, combinés à des restrictions sur les importations, ont maintenu une
pression significative sur les prix, tandis que l'offre marginale s'appuyait de plus en plus sur
les exportations américaines.

D'après les prévisions récentes, l'offre mondiale de GPL devrait atteindre 379,52 millions de
tonnes en 2024, marquant une croissance de 2,57 %. Cette tendance devrait se poursuivre
en 2025, avec une augmentation supplémentaire de l'offre mondiale estimée à
12,34 millions de tonnes.

1.2.1.3. Echanges mondiaux de GPL

En 2023, le commerce international de GPL a maintenu sa dynamique ascendante, avec une
offre exportable largement dominée par les États-Unis, tandis que la demande
d’importation demeurait fortement soutenue par l’Asie.

L’Amérique du Nord s'est imposée en tant que principal moteur de la croissance des
exportations de GPL, enregistrant une hausse de 9 millions de tonnes en variation annuelle.
Cette progression trouve son origine dans une production abondante, des capacités de
stockage colossales, ainsi que le développement et l’exploitation à pleine capacité des
infrastructures portuaires dédiées à l'exportation, en particulier aux États-Unis. Par ailleurs,
malgré les réductions de production décrétées par l'OPEP+, les exportations provenant des
pays du Golfe ont progressé de 1,14 million de tonnes en glissement annuel, portées par une
augmentation des expéditions iraniennes, et ce, en dépit des sanctions occidentales.
Ensemble, l'Amérique du Nord et les pays du Golfe totalisent plus des trois quarts des
exportations mondiales de GPL.

Une augmentation des exportations a été observée dans la région méditerranéenne, tandis
que les chargements de GPL en provenance de la Russie et des pays d'Europe de l'Est se
sont stabilisés par rapport à l'année 2022. En revanche, l'Europe du Nord-Ouest a connu la
plus forte baisse des exportations de GPL, avec une diminution de 0,98 million de tonnes en
2023 par rapport à l'année précédente. Cette baisse est principalement imputable à la
réduction de la production des raffineries, ainsi qu'à une baisse de la production issue du
traitement du gaz, notamment en Norvège.

=
Poids dans les exportations du GPL Poids dans les importations du GPL
par région en 2023 par région en 2023
Amérique du Nord Asie Pacifique 59,6%
46,6%

Moyen-Orient Nord-Ouest de l'Europe 13,0%
Nord-Ouest de l'Europe Méditerranée 10,6%

Méditerranée Amérique du Nord 7,9%

Asie Pacifique Amérique latine 5,8%

Afrique Afrique | 2,1%

Russie et l'Europe de l'est Russie et l'Europe de l'est | 1,0%

Amérique latine Moyen-Orient | 0,1%

#

Source : ElA, Aramco, Argus, IHS Merkit, Direction Norvégienne du pétrole, Platts

N



RAPPORT SUR COMPENSATION

Concernant les importations, l’Asie Pacifique reste le consommateur principal de l’offre
exportable avec près de 60 % des importations mondiales en 2023.

Pour les cinq principaux importateurs mondiaux de GPL, à l'exception de la Corée du Sud,
qui a enregistré une baisse de ses importations de 0,65 MT, les autres pays ont augmenté
leurs volumes d'importation, bien que de manière inégale. La Chine, premier importateur
mondial de GPL, a accru ses besoins extérieurs de plus de 25 % en glissement annuel,
atteignant ainsi 28,72 MT en 2023, grâce à ses vastes capacités de stockage. En ce qui
concerne l'Inde, le Japon et l'Indonésie, leurs importations ont progressé respectivement de
2,4 %, 1,4 % et 0,3 % par rapport à l'année précédente.

Dans les autres régions, tandis que les importations méditerranéennes ont progressé de
0,77 million de tonnes en raison de l'augmentation des besoins pétrochimiques et de
l'expansion du marché résidentiel, d'autres zones, telles que l'Europe du Nord-Ouest,
deviennent de moins en moins dépendantes de l'approvisionnement extérieur en GPL,
conformément à la nouvelle politique énergétique européenne.

Pour l'année 2024, les exportations américaines de GPL ont atteint leur plus haut niveau
semestriel au cours du premier semestre. L'Asie demeure la principale destination du
propane, représentant 61 % des exportations totales, tandis que cette région n’a absorbé
que 35 % du butane américain exporté. Quant à l’Afrique, considérée comme un marché en
pleine expansion pour la consommation de GPL, notamment du butane, elle a capté 38 %
des exportations de butane, en grande partie grâce à la présence du Maroc et de l’Égypte,
respectivement quatrième et cinquième importateurs mondiaux de ce produit.

Alors que les exportations américaines ont maintenu leur dynamique ascendante, celles des
pays du Golfe demeurent fortement influencées par les politiques de l'OPEP+, avec une
concentration marquée sur le marché asiatique. Toutefois, l’offre américaine gagne
progressivement des parts de marché auprès des clients traditionnels du GPL, notamment
l'Indonésie, tandis que les pays du Moyen-Orient ont perdu des parts en Chine. En effet, le
GPL américain a représenté 55 % des importations chinoises au cours du premier semestre
2024. De plus, le Japon et la Corée du Sud sont désormais majoritairement approvisionnés
par les États-Unis.

Avec moins de 10,6 millions de tonnes (MT) exportées au cours du premier semestre 2024,
en comparaison avec les exportations américaines, l'offre en provenance du Moyen-Orient
reste largement destinée aux clients asiatiques, en particulier au sous-continent indien.

Evolution semestrielle des Evolution des exportations mensuelles
exportations américaines du GPL des pays du Golf (MT)
(MT)
4,41
323 334 392 897 419 394
301 3,68
262 269 274 278 322

$ H $ 4 $ y jan-24 fév.-24 mar.-24 avr-24 mai-24 jui.-24 juil.-24

Source :ElA et Argus



Il convient de noter que la réduction du nombre de passages par le Canal de Panama à la
fin de 2023 et au début de 2024, due à la baisse du niveau des eaux, a eu un impact
temporaire sur les échanges mondiaux de GPL. Toutefois, le retour à la normale du trafic à
partir du mois de février a été observé avant que l'ouragan Beryl ne provoque des
perturbations sur les ports d'exportation américains de GPL au début de juillet 2024. Malgré
ces événements, la Chine a importé environ 2,7 millions de tonnes (MT) supplémentaires de
janvier à juillet 2024, par rapport à la même période en 2023, tandis que l'Inde a enregistré
une hausse de O,8 MT sur un an, en raison des élections ayant eu lieu au cours de la
première moitié de l'année. À l'inverse, les importations japonaises ont diminué de 0,35 MT
en glissement annuel pour la même période, en raison du niveau élevé des stocks finaux par
rapport à l'année précédente.

f
Evolution des importations des quatres premiers importateurs mondiaux du
GPL (MT)
18,96
1628
10,61
9,81
640 605
E '
Corée du Sud Japon Inde Chine
@ mJanvier-juillet 2023 » Janvier-juillet 2024

Source : Argus et Platts
1.2.2. Evolution des cours mondiaux du gaz butane
»> Evolution du cours du gaz butane en 2023

En 2023, le cours annuel moyen du gaz butane, suivant la formule marocaine, s’est élevé à
546 $/T, soit une baisse de 193 $/T par rapport au pic enregistré en 2022.

Après une forte baisse des cours du gaz butane au deuxième trimestre de l’année 2023,
causée par le net recul de la demande pétrochimique mondiale, la formule marocaine du
gaz butane s'est alignée sur sa trajectoire saisonnière habituelle durant le second semestre.

En octobre, sous l’effet du recul des cours du Brent et du WTI, la formule marocaine a
enregistré une diminution de plus de 32 $/T en variation mensuelle, s’établissant ainsi à une
moyenne de 534 $/T. Avec le début effectif de la haute saison de la demande en Europe et
la hausse des besoins américains en gaz butane pour les mélanges d’'essence, la formule
marocaine a augmenté de 7 $/T en novembre, atteignant 541 $/T.

En raison de la flambée des prix en Asie, partiellement causée par la restriction du passage
des navires de type VLGC par le Canal de Panama, la formule marocaine a augmenté en
décembre de près de 51 $/T en variation mensuelle, reflétant ainsi les pressions haussières
sur les prix à l'échelle mondiale, bien que le climat doux en Europe et en Méditerranée ait
réduit la demande de chauffage dans un contexte d'augmentation des stocks dans ces
deux régions.

S



RAPPORT SUR LA COMPENSATION

Evolution trimestrielle du cours du gaz Evolution annuelle du cours du gaz
butane suivant la formule marocaine butane ($/T)
en 2021-2023

739
890
792 831 634
686 546
s43 619 613 ° 7 P2
516 423
412 s7
l | l | |
S A 49 AN 0N MPMNMDM l | l
&,&WŒQW°N°W°Œ,‘(@«&1°WQŒ l

v v q A VVnF '\,
v = L
SS SIS 2015 2016 2017 2018 2019 2020 2021 2022 2023

Source : Platts et OPIS

» Evolution du cours du gaz butane en 2024

Les prix régionaux du gaz butane en 2024 ont suivi la tendance saisonnière habituelle, mais
avec une volatilité moins marquée que l’année précédente. En effet, tandis qu'en 2023 les
reculs de prix dépassaient 40 % entre les pics du premier trimestre et les niveaux les plus
bas, ceux de l’année 2024 n'ont pas excédé 14 % au cours des neuf premiers mois.

Au titre du premier trimestre, les principaux benchmarks mondiaux ont progressé en ligne
avec la tendance saisonnière en janvier et février, avant de connaître une évolution
contraire aux attentes du marché en mars. Malgré la baisse des prix en Asie et aux États-
Unis, l'Aramco a maintenu ses prix inchangés en mars, tandis que la Sonatrach a augmenté
ses tarifs de 40 $/T en variation mensuelle pour atteindre, en ce mois, le plus haut niveau
du prix algérien en un an

Entre avril et juillet, les prix régionaux du gaz butane ont suivi une trajectoire baissière
saisonnière, avec des baisses respectives de 80, 71, et 70 $/T pour les prix méditerranéen,
européen et saoudien entre mars et juillet.

À partir d'août, les principaux repères régionaux du prix du gaz butane ont amorcé une
hausse non saisonnière, atteignant des sommets pluri-mensuels. En particulier, le prix de la
Mer du Nord a atteint son plus haut niveau en cinq mois, en raison des achats importants du
secteur du vapocraquage, parallèlement à une fermeture de l’arbitrage transatlantique,

imitant ainsi les importations européennes en provenance des États-Unis.
( A
Evolution des prix mensuels en 2024 des principaux producteurs mondiaux du
GPL
490 425
. ' I . i i i° i l
Mars Juin Juillet Aout Septembre*
® Arabie Sunudlte IAlgelle #MerduNord BUSA*

Source : Platts et Argus Media (*Hors terminalling ;** jusqu’au le 15 septembre 2024)

N



» Evolution du cours du gaz butane suivant la formule marocaine en 2024

Au titre de la période janvier-août 2024, la formule marocaine du gaz butane s'est inscrite
dans une fourchette comprise entre 445 $/T et 601 $/T, avec une moyenne de 537 $/T,
contre 541 $/T en glissement annuel, enregistrant ainsi une légère baisse de 0,8 %. La
formule marocaine a suivi une tendance haussière au cours des huit premières semaines de
l’'année, conformément à son schéma saisonnier habituel, et durant la deuxième quinzaine
de mars. Cependant, à partir de la deuxième semaine d'’avril, la tendance s'est inversée
jusqu'au début juin, en raison d'une offre abondante et d'une demande considérablement
affaiblie. La perturbation de l'infrastructure d’exportation américaine a interrompu cette
baisse pendant près d'un mois, avant que la formule marocaine se stabilise dans une
fourchette comprise entre 507 $/T et 566 $/T durant les mois de juillet et août.

Dans des conditions normales de marché, la tendance trimestrielle du cours du gaz butane
présente généralement une hausse au premier et au quatrième trimestre, suivie d'une
baisse au deuxième et au troisième trimestre de chaque année. En 2024, les moyennes
mensuelles des cours durant la haute saison ont été inférieures à celles de 2023, avant que
les cours moyens mensuels des deuxième et troisième trimestres de 2024 dépassent leurs
équivalents en variation annuelle.

Evolution de la formule marocaine Evolution mensuelle de la formule
du gaz butane en 2024 ($/T) marocaine du gaz butane ($/T)
600
594 592 712
673
623
583
572 ssg 563 5 544 — s3
499 519,
464
446
427
374

SESS SS SS S SS S SN NN ; !

228292822222 28228282828 ; n

S9S99SSSSSSSSSSSS Janvier février mars avril mai — juin juillet août

939959 TTDDDOSONNàS

s822929228882 2885588

9N2ZS9oN5S2S550ASTS m 2023 » 2024
(8585385848453848A8

Source : Platts et OPIS

L'instabilité notable de la formule marocaine, fondée sur une moyenne pondérée des
composantes américaine (70 %) et euro-méditerranéenne (30 %), découle des fluctuations
des cours du gaz butane en provenance des États-Unis et de la région euro-
méditerranéenne. Toutefois, avec l'augmentation de la pondération de la composante
américaine, la formule s'est progressivement stabilisée en atténuant l'impact de la volatilité
de la composante euro-méditerranéenne.

N



»  La composante américaine :

RAPPORT SUR LA COMPENSATION

Evolution de la moyenne mensuelle
en 2024 de la composante américaine
($/T)

Evolution du rapport mensuel
moyen du prix du butane américain
par rapport au WTI

68,7% 67,6%

62,4%
59,3% 55,5% 56,4% 59,0%
l | 51,5% | l l

JanvierFévrier Mars Avril Mai Juin Juillet Août

566 575
537 529 507 535 531

Janvier février mars avril mai juin juillet août

Source : Platts, OPIS et Bloomberg

En janvier 2024, le prix du butane américain s'est stabilisé en variation mensuelle,
atteignant 566 $/T, avant d’atteindre son niveau le plus élevé sur une période de onze mois
en février 2024. Cette tendance haussière observée au cours des deux premiers mois
s’explique en grande partie par la hausse du cours du WTI, passé de 73,86 $/bbl en janvier
à 76,61 $/bbl, ainsi que par les conditions climatiques rigoureuses qui ont paralysé la côte
américaine du golfe du Mexique, en parallèle de l’interruption du trafic via le Canal de
Panama

Après un raleptissement du soutien habituel des prix par la demande de chauffage
hivernale aux Ftats-Unis durant les deux premiers mois de l'année, le prix du butane au
Golfe du Mexique a amorcé, à partir du mois de mars, un cycle saisonnier baissier. Ainsi, le
prix est passé de 575 $/T en février à 470 $/T en mai, marquant une baisse de plus de 18 %.
Cette évolution s'est produite malgré la hausse des cours du WTI en mars et en avril, en
raison des fondamentaux baissiers du marché. À cet égard, le rapport entre le prix du
butane à Mont Belvieu et celui du WTI est passé de 67,6 % en février à 51,5 % en mai.

Cette baisse s'explique par le recul de la demande liée aux mélanges d'essence de qualité
hivernale, en raison du redressement des températures aux États-Unis, ainsi que par
l'augmentation de la production pendant la période de constitution des stocks sur le
territoire américain. Parallèlement, la demande en provenance de certains pays (Maroc,
Indonésie et Égypte) s'est stabilisée, après avoir atteint un niveau record entre mi-février et
mi-mars, lorsque ces pays ont intensifié leurs importations en provenance des États-Unis
pour sécuriser l'approvisionnement durant le mois de Ramadan.

Contrairement au comportement saisonnier habituel, les prix du butane américain ont
amorcé leur cycle haussier prématurément cette année. En effet, le cours du butane aux
États-Unis a enregistré une hausse de 37 $/T en glissement mensuel, atteignant ainsi 507
$/T au mois de juin. Cette évolution résulte de l’anticipation de l’ouragan Beryl, qui s'est
formé dans l'Atlantique et s'est rapidement intensifié en un ouragan majeur avant de
frapper, pour la première fois, le Golfe du Mexique le 8 juillet. Cet événement a entraîné une
augmentation du prix moyen mensuel de juillet de 28 $/T et a relevé le rapport entre le prix
du butane et celui du WTI de 2,6 % en glissement mensuel.

Malgré la baisse significative du cours du WTI en août, qui a reculé de 5 $/bbl en glissement
mensuel, le prix du butane américain n'a diminué que de 4 $/T, pour s'établir à 531 $/T. De



surcroît, les prix du butane sur la côte américaine du Golfe du Mexique ont atteint, à la fin
du mois d'août, leur plus haut niveau en quatre mois. Cette hausse s'explique par une
demande soutenue à l'exportation et par un démarrage précoce des achats pour la saison
de mélange d'essence d'hiver - qui débute généralement à la mi-septembre et se prolonge
jusqu'en mars - aux États-Unis, ce qui a contribué à maintenir les prix élevés à la fin du mois
dernier.

» La composante euro-méditerranéenne :

Evolution de la moyenne mensuelle Evolution du rapport mensuel moyen
en 2024 de la composante euro- du prix du butane euro-méditérannien
méditérannienne ($/T) par rapport au Brent

s87 59 79,9% 79,0% 76,5%

601
554 567 556
482
450 |

Janvierfévrier mars avril mai juin juillet août

72,9% 76,0%

67,2%
l l l l“’”‘“i‘l l
Source : Platts, OPIS et Bloomberg

Le début de l'année 2024 a été marqué par des pressions baissières sur le marché euro-
méditerranéen du butane, transporté par des coasters. En effet, le niveau moyen de la
composante euro-méditerranéenne a reculé de 24 $/T en glissement mensuel au mois de
janvier, en raison du faible intérêt du secteur des mélanges d'essence, d'une demande
limitée pour les exportations de cargaisons en provenance de l'Europe du Nord-Ouest vers
la région méditerranéenne, ainsi que des flux élevés de butane américain vers cette région,
qui ont continué à restreindre la demande locale des Coasters.

En février et mars, le prix du gaz butane s'est stabilisé autour de 600 $/T, reflétant
l'augmentation de la demande dans la région euro-méditerranéenne à l'approche du mois
de Ramadan, ainsi que la hausse du cours du Brent. À cela s'ajoute la focalisation des
mélangeurs d'essence sur l'utilisation de petits navires, accompagnée d'une forte demande
émanant des acheteurs pétrochimiques européens.

Durant les mois d’avril et de mai, la composante euro-méditerranéenne a suivi, à l'instar des
autres prix régionaux, une tendance baissière, enregistrant un recul de 150 $/T entre mars
et mai. Cette baisse s'explique par la fin de la saison de chauffage au butane dans la région
euro-méditerranéenne et un intérêt modéré des acheteurs pétrochimiques, alors que l’offre
régionale a considérablement augmenté durant cette période.

En mai et juin, les prix FOB des coasters de la région euro-méditerranéenne sont passés en
dessous de ceux du butane américain, illustrant la fermeture de l'arbitrage avec les États-
Unis. Cela témoigne de la volonté des vendeurs locaux de liquider leurs stocks de butane et
d'empêcher toute importation en provenance des USA.

Le sentiment du marché s’est renforcé à partir de la deuxième quinzaine de juin, en raison
de la fermeture récente de l'arbitrage, limitant ainsi les approvisionnements américains,
combinée à la faiblesse de l’offre régionale. Dans ce contexte, la moyenne mensuelle de la
composante euro-méditerranéenne a augmenté de 32 $/T en glissement mensuel en juin,

N



RAPPORT SUR LA COMPENSATION

avant de connaître la plus forte hausse de l’année avec un bond de 85 $/T en juillet, suite à
la perturbation des plannings d’importations en provenance des États-Unis. Une accalmie
relative a ensuite marqué le marché euro-méditerranéen avec l'arrivée des cargaisons de
butane américain, ce qui a conduit à un recul de 11 $/T en glissement mensuel, stabilisant le
niveau moyen du cours à 556 $/T.

» Evolution du fret :

Le tarif du transport maritime entre les États-Unis (Houston) et le Maroc (port de
Mohammedia) a atteint en 2023 son niveau moyen annuel le plus élevé jamais enregistré,
s'établissant à 98 $/T, soit une augmentation de 27 $/T par rapport à l'année précédente.

N
( Evolution de taux de fret Evolution des moyennes mensuelles du
annuel moyen pour les VLGC fret (VLGC) pour le trajet Houston-
(Houston-Mohammadia) Mohammadia

132

119 113 us
98
71
53 52 …
28 28 31 l l I
727 à R

2016 2017 2018 2019 2020 2021 2022 2023

Source : OPIS

Au cours des quatre derniers mois de l’année 2023, les taux de fret moyens mensuels entre
les États-Unis et le Maroc ont dépassé 113 $/T, atteignant un sommet historique en
novembre 2023. La baisse des niveaux d'eau du lac Gatun a conduit les autorités du canal
de Panama à limiter le nombre de transits, en particulier pour les Neopanamaxes,
provoquant d’importants retards pour les navires empruntant cette voie. En conséquence,
de nombreux VLGC (Very Large Gas Carriers : Très grands transporteurs de gaz ) ont
modifié leurs trajectoires, optant pour le canal de Suez ou le cap de Bonne-Espérance.

Depuis décembre, le taux de fret a suivi une tendance baissière, enregistrant une diminution
de 63 $/T entre décembre ct février, soit une baisse de 55 %. Cette diminution est attribuée
à l'augmentation des prix du propane sur la côte américaine du Golfe du Mexique, causée
par la réduction des stocks et des problèmes logistiques à une période de forte demande
de chauffage. De plus, la réorientation des VLGC, évitant le canal de Panama en raison des
tensions croissantes en mer Rouge, a contribué à cette baisse. Les autorités portuaires du
canal de Panama ont néanmoins réduit les temps d'attente, diminuant ainsi la dépendance
aux itinéraires plus longs et risqués via le cap de Bonne-Fspérance ou le canal de Suez. En
règle générale, les tarifs des VLGC, dans des conditions logistiques normales, montrent une
corrélation négative avec les prix du GPL américain, en particulier ceux du propane.

Avec la baisse des cours du butane et du propane dans le Golfe du Mexique à partir de
mars, le coût du transport vers le Maroc a commencé à augmenter, atteignant son niveau
mensuel moyen le plus élevé en mai 2024. Cependant, les taux de fret ont ensuite diminué
entre juin et août en raison des répercussions de l'ouragan Beryl sur les infrastructures
portuaires américaines. Il est important de souligner que les tarifs de transport des États-
Unis vers le Maroc sont étroitement alignés sur ceux des principales routes (États-Unis vers
l'Asie et Moyen-Orient vers l’Asie), en raison de la disponibilité limitée de la flotte maritime
spécialisée dans le transport de GPL et du rôle prépondérant de l'Asie dans la demande

mondiale.



1 1.3. Marché sucrier
1.3.1. Commerce international du sucre

1.3.1.1. Production et consommation mondiales du sucre

Le marché mondial du sucre demeure tendu au titre de la campagne sucrière 2023/24 en
raison de la succession des campagnes déficitaires ou faiblement excédentaires ces
dernières années, les politiques restrictives d’exportations empruntées par certains pays
surtout l’Inde, les tensions logistiques suite à l'engorgement des ports du Sud brésilien et au
niveau de la mer Rouge et la mer Noire, les incertitudes climatiques liées essentiellement
au phénomène climatique El Nino et la poursuite de l'envolée des prix de l’énergie par
rapport à leurs niveaux conventionnels. La combinaison de ces facteurs, a continué
d’exercer une pression sur les cours mondiaux du sucre brut.

Après avoir atteint des niveaux de prix élevés en 2022 et surtout en 2023, les cours
mondiaux du sucre ont connu une baisse progressive sur les huit premiers mois de l’année
2024, mais tout en restant dans des niveaux supérieurs par rapport aux années d'excédent
de production mondiale de ce produit. Ledit repli, s'explique essentiellement par une
production brésilienne de canne à sucre record pour la campagne 2023-2024.

» Production mondiale du sucre :

La production mondiale de sucre pour la campagne 2023/24 (depuis octobre 2023 à
septembre 2024) est estimée à 181,263 MT soit une augmentation de 1,98% par rapport à
l’'année précédente. La production historique du Brésil au titre de cette campagne, ct la
reprise dans l'Union européenne et la Chine ont compensé les baisses prévues en Inde et en
Thaïlande.

Environ 80 % de cette production provient de la canne à sucre. Le Brésil, premier
producteur et exportateur de sucre au monde, a renforcé sa position au cours de cette
campagne, en étant la principale source d'approvisionnement pour la plupart des pays au
niveau mondial.

Les principaux producteurs de sucre sont le Brésil, l'Inde, l'Union Européenne et la
Thaïlande pour la canne à sucre, tandis que pour la betterave, les principaux producteurs
sont l'Union Européenne, la Russie et les États-Unis. Les cinq premiers producteurs au
monde s'accaparent d'environ 56 % de la production mondiale.

Principaux producteurs mondiaux du sucre pour la campagne 2023/24
4%
5%
8%
17%
mBrésil “Inde UE — Chine “ Thaïlande

Source : WILMAR / SUCDEN

Selon les données de l'Organisation Internationale du Sucre (ISO) pour la campagne
2023/24 (octobre 2023 à septembre 2024), plusieurs pays ont connu des variations
significatives dans leur production de sucre par rapport à la campagne 2022/23.

yN



RAPPORT SUR LA COMPENSATION

Certains pays ont enregistré une augmentation de la production. Au Brésil, la production
est passée à 38,1 MT en 2023/24 contre 37,1 MT en 2022/23, soit une hausse de 3%, grâce à
une plus grande disponibilité de canne à sucre et à une orientation accrue vers la
production de sucre plutôt que d'éthanol. Au niveau de l'Union Européenne, la production
du sucre a augmenté en s'élevant à 17,1 MT contre 16,2 MT au titre de la campagne
précédente, soit une montée de 6%, grâce à des conditions climatiques favorables et à une
meilleure gestion des cultures. En Chine, la production a augmenté à 11,6 MT contre 10,6 MT
au titre de la campagne précédente, soit une hausse de 9%, en raison de l'expansion des
surfaces cultivées et des améliorations techniques agricoles.

En revanche, en Thaïlande, la production est passée à 7,75 MT en 2023/24 contre 10,0 MT
en 2022/23, marquant une baisse de 23% due à une sécheresse persistante et à des
récoltes anticipées. En Inde, la production s’est repliée à 33,2 MT en 2023/24 contre 34,3
MT en 2022/23, soit une baisse de 3%, causée par des précipitations irrégulières et une
gestion inefficace des ressources hydriques. Le Mexique a également enregistré une chute
de production au titre de cette campagne à 5,77 MT contre 6,35 MT au titre de la campagne
précédente, soit une diminution de 9%, en raison de conditions climatiques défavorables.

» Consommation mondiale du sucre

Selon l'ISO, la consommation mondiale de sucre atteindrait 181.463 MT pour la campagne
2023/2024, en hausse de 1,43% par rapport à la campagne précédente. L’essentiel de cette
croissance vient de l'Afrique et d’Asie. De ce fait, le déficit en termes de bilan sucrier
mondial s’élève à O,2 MT. Les principaux consommateurs sont l'Inde, l'Union Européenne et
la Chine. Entre 2011 et 2016, la consommation mondiale a connu une augmentation
soutenue de 1,4 % à 2,4 % par an. Cette hausse a été plus modérée entre 2017 et 2019 en
baissant à 0,8 %, avant de reprendre à un rythme de 0,5 % à 1,7 % par an depuis 2021, après
une chute liée à la pandémie de COVID-19 en 2020.

La demande de sucre est influencée par divers facteurs, tels que la croissance
démographique, les revenus par habitant, le prix du sucre à New York par rapport à
l'isoglucose et aux édulcorants alternatifs, l'accessibilité au dollar, ainsi que les débats sur
les problèmes de santé. Les politiques gouvernementales qui régissent l'industrie sucrière,
incluant la présence ou l'absence de subventions et le prix de vente public du sucre, jouent
également un rôle crucial. Tous ces éléments, parmi d'autres, interagissent pour façonner
les tendances de la demande sur le marché international du sucre.

Les cinq principaux consommateurs s’accaparent de 46 % de la consommation mondiale de
sucre. En effet, l'Inde occupe une part de 16 % de la demande mondiale, tandis que l'Union
européenne, la Chine et les États-Unis représentent respectivement 10% ,9% et 6 % de
l'utilisation mondiale dudit produit.

Principaux consommateurs mondiaux du sucre pour la campagne 2023/24

5%
6%

10%

Hinde “UE - Chine - USA » Brésil

Source : WILMAR / SUCDEN



1.3.1.2. Echanges mondiaux de sucre

Les régions de l'Amérique du Nord, de l'Amérique du Sud et du sous-continent indien
affichent structurellement un excédent de sucre, tandis qu'un déficit structurel est observé
en Afrique, au Moyen-Orient et dans la région Asie-Pacifique-Océanie. Pour la saison
2023/24, les échanges mondiaux de sucre sont estimés à 64 MT, dont 62% de sucre brut et
38 % de sucre blanc. Ce niveau représente 34 % de la production mondiale au vu qu'il s’agit
d'un produit résidentiel. Le maintien de ce niveau conventionnel revient à l’augmentation
des disponibilités exportables au Brésil, qui fera plus que compenser la baisse prévue des
exportations de la Thaïlande et l’arrêt de celles en provenance de l'Inde.

Du côté des importations, des achats plus importants de l’Asie et de l'Afrique devraient
compenser une forte baisse probable en Europe. En Chine, plus grand acheteur de sucre au
monde, les autorités prévoient que les importations augmenteront par rapport à l’année
dernière, malgré la reprise de la production nationale. En revanche, les importations de
sucre par l'Union européenne devraient diminuer sensiblement par rapport à l’année
dernière en raison d’une production intérieure plus élevée.

En somme, les flux commerciaux de sucre brut sont principalement dirigés de l'Amérique
centrale et du Sud vers l'hémisphère est (Asie et Afrique). Pour le sucre blanc, les
importations se concentrent dans la région MENA, le Far East (Chine, Japon, Corée du Sud,
Taïwan), l’Afrique de l'Est et l'Afrique de l'Ouest. Les exportations de sucre blanc
proviennent principalement du Brésil, de la Thaïlande et de l'Union Européenne, avec une
absence notable des exportations indiennes pour cette saison.

Principaux exportateurs mondiaux du sucre pour la campagne 2023/24

5% 2%
8%

52%

mBrésil — Thaïlande “ Australie Guatemala

Source : WILMAR / SUCDEN

En somme, le bilan mondial de sucre se présente comme suit :

Evolution du bilan sucrier mondial (MT)
171 170 169 171 173175 178 179 181 181
97,6 96,6 100 99 99
0,9 |
2019-2020 2020-2021 2021-2022 2022-2023 2023-2024
© Production M Consommation m Surplus/Déficit Stocks finaux

Source : ISO

N



RAPPORT SUR LA COMPENSATION

1.3.2. Evolution des cours mondiaux du sucre brut

Au cours des cinq dernières années, le cours du sucre brut s'est inscrit dans une tendance
haussière continue et prononcée. || est passé d’une moyenne de 295 $/T en 2019 pour
atteindre 566 $/T en 2023, soit une flambée de 92%. Cette montée vertigineuse est
imputable à plusieurs facteurs dont essentiellement, l’évolution des politiques de commerce
extérieur de certains pays producteurs (restrictions d’exportation), l’envolée des cours du
pétrole brut d’où le recours à la production d’éthanol, les problèmes logistiques et le déficit
de la production mondiale du sucre.

Evolution annuelle des cours du sucre brut ($/T)
566

295 307

2019 2020 2021 2022 2023

Source : Bloomberg adapté.

»  Evolution des cours du sucre brut en 2024

Les cours du sucre brut ont varié, au titre de la période allant du 1°” janvier au 31 août 2024,
dans une fourchette allant d'un minimum de 416 $/T et un maximum de 575 $/T, soit une
moyenne de 483 $/T, marquant une baisse de 12 % par rapport à la même période en 2023
Ainsi, l’évolution trimestrielle des cours dudit produit s’est présentée comme suit :

Premier trimestre 2024 : le cours mondial du sucre brut s’est caractérisé par une forte
volatilité durant ledit trimestre en enregistrant une moyenne de 531 $/T. Une tendance
haussière a été observée au titre des deux premiers mois de l'année en atteignant un pic de
575 $/T le 24 janvier. A partir du début du mois de mars, les cours ont chuté à un minimum
de 486 $/T avant de remonter à nouveau à plus de 530 $/T vers la fin du mois.

Cours du sucre au titre du premier trimestre 2024 ($/T) D
575
565 564
530
493
486
02/01/2024 17/01/2024 01/02/2024 16/02/2024 02/08/2024 17/03/2024

Source : Bloomberg adapté.

»N



Deuxième trimestre 2024: Durant le deuxième trimestre de l’année 2024, le cours du sucre
a connu des fluctuations significatives en oscillant entre un minimum de 429 $/T et un
maximum de 535 $/T. En effet, la valeur moyenne sur cette période s'est établie à 462 $/T,
en baisse de 13 % par rapport au trimestre précédent. Après une baisse notable en avril et
mai, le cours du sucre brut a repris progressivement en juin, montrant une tendance
générale de stabilisation et de légère hausse en fin de trimestre.

Cours du sucre au cours du deuxième trimestre 2024 ($/T)
535

454

455
429

01/04/2024 16/04/2024 01/05/2024 16/05/2024 31/05/2024 15/06/2024

Source : Bloomberg adapté.

Juillet-août 2024 : les cours du sucre brut ont amorcé une tendance baissière au cours des
mois de juillet et août 2024 en se repliant à un minimum de 416 $/T avant de remonter
progressivement vers la fin du mois à près de maximum de 469 $/T.

Evolution des cours du sucre au titre de la période juillet- août 2024 ($/T)

466 469
451
435

423 416

01/07/2024 16/07/2024 31/07/2024 15/08/2024 30/08/2024

Source : Bloomberg adapté.

1.4. Marché céréalier

1.4.1. Commerce international des céréales

1.4.1.1. Production et consommation mondiales des céréales

» Production mondiale des céréales

Selon les données de la FAO publiées le 6 septembre 2024, la production mondiale de
céréales, au titre de la campagne 2023/24, s'’est élevée à un niveau de 2.852,8 MT,

enregistrant une hausse de 1,39 % par rapport à la campagne précédente, soit un niveau
quasi équivalent à l’année précédente.

S'agissant de la production mondiale de céréales secondaires en 2023/24, elle s’établit à
1.532,5 MT, en hausse de 3,4 % sur une base annuelle. La production mondiale d'orge pour
la campagne 2023/24 est revue à la hausse, principalement en raison de conditions
météorologiques favorables dans certaines régions productrices clés, à savoir l'Union

N



RAPPORT SUR LA COMPENSATION

Européenne et la Russie. De plus, la demande accrue pour l'alimentation animale stimule
cette augmentation de production. Les données indiquent également une hausse de la
production de riz pour la campagne 2023/24 atteignant 530,1 MT. Cette augmentation est
due à l'expansion des surfaces cultivées et à l'amélioration des rendements dans des pays
asiatiques comme l'Inde et la Chine.

cette année une baisse de 2,18% par rapport à l’année précédente, sous l'effet des récentes
conditions météorologiques défavorables dans la région de la mer Noire, mais demeure à
des niveaux supérieurs par rapport aux campagnes 2020/21 et 2021/22.

Evolution annuelle de la production mondiale (MT)

2773,7 2809,1 2813,8 2852,8 2851,4
© 7ä 8ä 7ä 7ä
2020/21 2021/22 2022/23 2023/24 (*) 2024/25 (**)

Production Blé … M Production Céréales

Source : FAO (* : estimation, ** : prévision)

La répartition de la production de blé pour la saison 2023/24 diffère d’une région
productrice à une autre. L'Union européenne est en tête avec une production de 133,1 MT.
La Russie s’accapare une quantité de 91 MT, affirmant ainsi son rôle clé sur le marché
international du blé. Les États-Unis ont produit 49,3 MT, tandis que le Canada a contribué
avec 32 MT. L'Australie, l'Ukraine, l'Argentine et le Kazakhstan ont respectivement produit
26, 28,4, 15,9 et 12,1 MT.

Production de blés des principaux exportateurs 2023/24 (MT)

133,1
910
49,3
32,0 28,4
- s20 159 124
UE Russie uUsa Canada Australie Ukraine Argentine — Kazakhstan
Source : IGC

Pour la campagne 2024/25, les analystes du marché tablent sur une augmentation de la
production de près de 3 MT. Cette progression est principalement attribuée à des résultats
meilleurs que prévu aux États-Unis, où la récolte d'hiver est presque achevée, ainsi qu'à des
révisions à la hausse des prévisions de production en Chine continentale et en Argentine,
bien que plus modestes. Ces augmentations ont été partiellement compensées par des
révisions à la baisse des prévisions de production de blé dans l'Union européenne, en raison
de conditions climatiques trop humides, et en Russie, où des conditions météorologiques
défavorables ont entraîné une baisse des rendements.



» Utilisation mondiale des céréales

L'utilisation mondiale de céré pour la campagne 2023/24, s’élève, selon le
dernier rapport de la FAO datant du © septembre, à 2.846,55 MT, soit une
augmentation de 2% par rapport à la campagne 2022/23. Cette croissance est
essentiellement imputable à l’augmentation de l'utilisation de céréales secondaires
et de blé, sous l’effet de l’abondance de l’offre et de la baisse des prix par rapport
à la campagne précédente, tandis que l’utilisation de riz a très légèrement reculé.

2022/23, en raison de la hausse de la demande pour l'alimentation animale, en
particulier dans les régions où le maïs est moins disponible ou plus coûteux, et à la
croissance démographique mondiale continuant d'augmenter la demande de blé,
un aliment de base dans de nombreuses régions du monde.

Evolution annuelle de l'utilisation mondiale (MT)

2762,9 2788,6 2790,9 2846,5 2851,8
763,3 | l 770,3 I l 7774 | l 798,2 | l 798,3 I l
2020/21 2021/22 2022/23 2023/24 (*) 2024/25 (**)

mUtilisation blé » Utilisation céréales

Source : FAO (* : estimation, ** : prévision)

Concernant l'utilisation de céréales secondaires pour la campagne 2023/24, elle
s’élève à 1.522,3 MT, en hausse 2,39 % par rapport à la campagne précédente.
Cette évolution est principalement expliquée par la hausse attendue de l'utilisation
du maïs, en particulier à des fins d’alimentation animale.

1.4.1.2. Stocks et échanges mondiaux des céréales
» Stocks mondiaux des céréales
D’après la FAO, les stocks mondiaux des céréales en 2023/24 se situent à 878,9

MT, en hausse de 6 MT (équivaut à 0,69%) par rapport à la campagne précédente.

Concernant les stocks mondiaux de blé, ils se sont élevés à 3151 MT lors de la
campagne 2023/24 contre 323,2 MT en 2022/23, soit une baisse de 2,51 %.

Evolution annuelle des stocks mondiaux (MT)

836,4 8583 8729 878,9 889,7
5 ziül 3ä 3ä 3Æ
2020/21 2021/22 2022/23 2023/24 (*) 2024/25 (**)

# Stocks blé_ M Stocks céréales

Source : FAO (* : estimation, ** : prévision)

N



RAPPORT SUR LA COMPENSATION

Quant aux stocks de céréales secondaires, ils ont reculé de 1,24% par rapport à la

campagne précédente pour atteindre 365,9 MT au terme de ladite campagne.

» Echanges mondiaux des céréales

Selon la FAO, le commerce mondial des céréales a progressé de 4,74 %, en s'élevant à
502,1 MT au titre de la campagne 2023/2024 contre 479,4 MT au titre de la campagne
2022/23.

Quant aux échanges mondiaux du blé, ils ont augmenté de 2,58%, en enregistrant 207,0 MT
au titre de la campagne 2023/2024, contre 201,8 MT au titre de la campagne 2022/23.

Evolution annuelle des échanges mondiaux (MT)

482,5 483,2 479,4 502,1 485,6
189,9 l l 1968 l | 2018 l l 207,0 l l 199,4 | |
2020/21 2021/22 2022/23 2023/24 (*) 2024/25 (**)

mEchanges blé _ Echanges céréales

Source : FAO (* : estimation, ** : prévision)

S'agissant des échanges mondiaux des céréales secondaires en 2023/24, ils ont atteint
243 MT, ce qui représente une hausse de 4,34% par rapport à la campagne 2022/23.

Pour la campagne 2023/24, la production du blé est estimée à 7885 MT contre une
demande plus supérieure s’élevant à 798,2 MT. Cette situation a induit une baisse
remarquable des stocks finaux de blé à 315,1 MT.

Bilan mondial du blé pour la campagne 2023/24 (MT)

788,5 798,2
315,1
Production Utilisation Echanges Stocks finaux
Source : FAO

1.4.2. Evolution des cours mondiaux du blé tendre

Le cours du blé tendre d’origine française a enregistré une forte volatilité au cours des cinq
dernières années en raison essentiellement des répercussions de la pandémie de covid-19 et
les perturbations géopolitiques, climatiques et logistiques.

Il s’est inscrit dans une tendance haussière continue depuis l’année 2019 en passant d’un
cours minimum de 207 $/T à un pic de 366 $/T en 2022 en raison du conflit russo-
ukrainien

En 2023, le cours mondial du blé tendre a amorcé une baisse progressive en raison de
plusieurs facteurs : la reprise des exportations ukrainiennes grâce à un accord de l'ONU, et
de bonnes conditions météorologiques qui ont permis des récoltes abondantes en
Amérique du Nord, en Europe et en Russie, augmentant ainsi l’offre sur le marché.



-

—
Evolution annuelle des cours moyens du blé tendre d'origine française ($/T)
366
291
267
226
207
2019 2020 2021 2022 2023
Source : IGC

» Evolution des cours du blé tendre en 2024:

Les cours du blé tendre d'origine française ont oscillé, au titre de la période allant du 1°"

janvier au 31 août 2024, dans une fourchette comprise entre 206 et 275 $/T, soit une
moyenne de 233 $/T.

Evolution mensuelle du cours du blé tendre Fr-Gr2 ($/T)
275
245
234
227
221
206
01/01 01/02 01/03 01/04 01/05 01/06 01/07 01/08
Source : IGC



RAPPORT SUR LA COMPENSATION

CHAPITRE Il: EVOLUTION DE LA CHARGE DU
SOUTIEN DES PRIX DES PRODUITS
SUBVENTIONNES

IL.1. Soutien du prix du gaz butane
11.1.1. Evolution des subventions unitaires du gaz butane

» Evolution annuelle des subventions unitaires du gaz butane

La subvention annuelle moyenne, au titre de l’année 2023, octroyée pour une bonbonne de
gaz butane de 12 kg, a enregistré une baisse significative de 25 DH sur une base annuelle.
Celle-ci représentait 63 % du prix de vente au consommateur, atteignant ainsi une moyenne
de 69 DH en 2023, soit le deuxième niveau le plus élevé des neuf dernières années.

Subvention unitaire annuelle moyenne de la bonbonne de 12 Kg du gaz butane
(DH)

94

2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023

» Evolution des subventions unitaires du gaz butane au titre de la période
janvier-septembre 2024

Sur la période allant de janvier à septembre 2024, la subvention accordée pour la
bonbonne de 12 kg a fluctué entre 47 et 75 DH, avec une moyenne de 61 DH. Cette
moyenne représente un repli de 10,3 % (7 DH) par rapport à la même période de l'année
précédente.

Durant les sept premiers mois de 2024, la subvention de l'État a suivi une tendance
baissière, atteignant son point le plus bas en juin. Cette évolution reflète la trajectoire des
cours du gaz butane, marquée par des baisses mensuelles successives jusqu'au minimum
annuel.

Cependant, au troisième trimestre, cette tendance s’est inversée, avec une augmentation de

la subvention, qui a dépassé les 50 DH, malgré la hausse des prix de vente en mai 2024 et
e recul de 3,4 % du taux de change entre avril et août.

Evolution de la Subvention mensuelle de la bonbonne de 12 Kg (DH)

75
72 m0
69 &
57
s6 s4 52
47
jan-24 fév-24 mar-24 avr-24 — 01-19mai 20-31mai — jui-24 jui-24 — août-24 — sept-24

yN



Au cours des neuf premiers mois de l'année 2024, la part subventionnée moyenne du gaz
butane a couvert 64 % du prix d'achat réel, marquant une baisse de 4 % en glissement
annuel.

Tableau : Taux de subvention du prix du gaz butane en 2024

20-31Mai Juin Juillet Août Sept

Janvier  Février Mars  Avril

Coût de revient réel DH/B 15 112 mo 109 107 107 97 100 104 102

Part de la subvention (%) 65% 64% 64% 63%  62% 53% 48% 50%  52% 51%

Part du prix de vente (%) 35% 36% 36% 37% 38% 47% 52% 50% 48%  49%

11.1.2. Importation et consommation nationales du gaz butane

»  Evolution des importations

Après une augmentation notable de 7,3 % en 2022, les importations nationales de gaz
butane ont enregistré une légère baisse de 0,7 %, soit une diminution de 20 KT, équivalente
à un bateau d'importation en provenance des États-Unis, pour s'établir à 2,76 MT.

Ce recul constitue le deuxième repli observé sur la période 2021-2023, principalement
attribué à l'aversion au risque liée à la dépréciation des stocks, une situation à laquelle les
opérateurs marocains ont été confrontés au cours des mois du dernier trimestre de l'année
2023, suite à la forte chute des cours. A l’exception de l’année 2021 et depuis 2010, le Maroc
a importé annuellement, en moyenne, 100 KT additionnelle pour satisfaire la croissance des
besoins du marché national alors qu’en 2022 cette quantité s’est élevée à 190 KT.

La structure des importations a connu des évolutions continues, influencées tant par les
circonstances internationales, telles que les arbitrages, la disponibilité de l'offre et les
facteurs géopolitiques, que par des dynamiques internes. Ces dernières incluent la variation

saisonnière de la demande, l'état des réserves nationales, l'infrastructure
d'approvisionnement du pays, ainsi que les conditions climatiques.
Les importations nationales Les importations du gaz butane par origine
du gaz butane (MT) (%)
76%
2,78 77%
2,76 H
50%
f 26%
23%
sé 24%
1% 0% 0%
p
2021 2022 2023 2024*
2017 2018 2019 2020 2021 2022 2023 HUSA wEurope " Algérie M Autres

*pour la période janvier-juin 2024
Source : Office des changes

N



RAPPORT SUR COMPENSATION

À partir de l'année 2022, la structure nationale d'importation de gaz butane a affiché une
stabilité caractérisée par la prédominance du produit en provenance des États-Unis, la
disparition des importations algériennes et un léger recul des importations européennes, au
profit des importations transatlantiques.

En 2023, le butane américain a couvert plus des trois quarts des besoins nationaux,
ilustrant la forte pénétration de ce produit sur le marché marocain. En effet, les
importations en provenance des États-Unis sont passées de 300 KT en 2017, représentant
13 % des importations, à 2.087 KT en 2023, ce qui correspond à une croissance remarquable
de 596 % au cours des sept dernières années. Bien que les importations nationales aient
diminué en 2023 par rapport à l'année précédente, les opérateurs gaziers marocains ont
importé 128 KT supplémentaires des États-Unis, renforçant ainsi les liens étroits entre le
marché marocain du gaz butane et celui des États-Unis.

Au cours du premier semestre de l'année 2024, les importations nationales se sont
stabilisées en glissement annuel, atteignant 1.461 KT. Afin de pallier la diminution des stocks
pendant la période du Ramadan, les opérateurs gaziers ont maximisé leurs importations en
avril, et le niveau d'importation est resté élevé en mai, dans le but de reconstituer les
réserves, tout en profitant d'une baisse significative des prix, de plus de 90 $/T, durant ce
mois.

La structure mensuelle des importations suit l'évolution des cours internationaux et les
engagements contractuels des opérateurs nationaux. Au cours des six premiers mois de
l'année, le produit américain a représenté plus de 74 % des importations mensuelles. Par
ailleurs, les produits espagnols et britanniques figurent presque mensuellement dans le
panier gazier national. Cette situation s'explique en grande partie par la capacité portuaire
limitée de certains sites d’importation, tels que Nador, Agadir et Laâyoune, où le produit
européen, principalement espagnol, demeure la principale source d'approvisionnement des
centres emplisseurs s'approvisionnant à partir de ces ports

En période de perturbation des exportations américaines, comme ce fut le cas en janvier
2024, ou lors de difficultés de réception au port de Mohammedia, qui reçoit 50 % des
importations totales, les opérateurs nationaux se tournent vers les importations
européennes, notamment espagnoles, en raison de leur proximité géographique et de la
taille adaptée des navires transportant le gaz butane à toutes les infrastructures portuaires
du Royaume. En outre, durant les périodes de forte demande, telles que le mois de
Ramadan, les gaziers marocains augmentent la part du butane espagnol, comme ce fut le
cas en mars et avril de cette année.

( Les importations mensuelles Evolution mensuelle des poids des sources
du gaz butane au titre du d'approvisionnement du gaz butane en S1-
premier semestre de 2024 (KT) 2024

76%

282 278
1 229 222 s0 74% Ec SRE 74%
208
18% ‘13% l°“ \14% \1% l4%
= 0 1S 99 MPu SS
$ 5 5 5 5 5

jan.-24 fév.-24 mar.-24 avr.-24 mai-24 jui.-24

\$\ ‘ HUSA “ Espagne “ Royaume-Uni m Autres pays européens

N



En matière d'exportations américaines de gaz butane, le Maroc s'est affirmé comme le
principal client des États-Unis au cours du premier semestre de l'année 2024, dépassant
ainsi des partenaires traditionnels tels que le Japon, la Corée du Sud et l'Indonésie. En effet,
au titre du premier semestre de l’année 2024, 15 % des exportations américaines de gaz
butane ont été destinées au marché marocain, contre 13 % en glissement annuel,

Les poids des principaux clients du butane américain en premier semestre de
l'année 2024

15%

Source : Administration américaine de l'Information sur l’Energie (ElA)
»> Evolution de la consommation

Depuis la fin du dernier millénaire, la consommation de gaz butane sur le marché marocain
a quasiment triplé, positionnant ainsi |le Royaume parmi les plus grands marchés mondiaux
pour ce produit. Cette progression de la demande nationale s'explique par divers facteurs,
tels que la croissance démographique, l'urbanisation accélérée, la forte accessibilité tant en
termes de prix que d'infrastructures de distribution, ainsi que l'amélioration des conditions
de vie.

En 2023, les Marocains ont consommé l'équivalent de 234,2 millions de bonbonnes de 12 kg,
soit 2,81 MT de gaz butane subventionné, marquant une augmentation de 6,9 millions de
bonbonnes de 12 kg en glissement annuel. Cette croissance de 2,93 % constitue la plus forte
hausse depuis 2020, année durant laquelle l'utilisation du butane avait considérablement
augmenté dans le secteur résidentiel en raison des mesures de restriction de la mobilité.

(

Evolution de la consommation
nationale en équivalent de millions de
bonbonnes de 12 kg

234,2

227,3
2219 2223
210,5
199,1
195,4 |

Evolution de la consommation
nationale du gaz butane (MT)

2,81
; 267 273
254 266

234 239

2017 2018 2019 2020 2021 2022 2023

2017 2018 2019 72020 2021 2022 2023

Source : Caisse de compensation

N



RAPPORT SUR LA COMPENSATION

11.1.3. Situation de la charge de compensation du gaz butane

» Charge de compensation du gaz butane en 2023

La forte diminution des cours du gaz butane en 2023, de plus de 26 % en glissement annuel,
a entraîné une réduction significative de la charge de compensation, qui a reculé de 23,4 %
pour s’établir à 16.737 MDH, soit une baisse de 5.075 MDH par rapport à l'année précédente.
Malgré cette contraction, l'enveloppe budgétaire allouée au soutien du gaz butane pour
'année 2023 demeure à son deuxième plus haut niveau historique, après celui enregistré en
2022.

Evolution annuelle de la charge de compensation du gaz butane (MMDH)

218
16,7
14,6
13,5
121
10,3 10,4
87 91
l 7'1 l l l

2014 2015 2016 2017 2018 2019 2020 2021 2022 2023

Source : Caisse de Compensation et HCP

Au cours des dix dernières années, l'État marocain a alloué 124,3 milliards de DH pour
soutenir les prix à la consommation du gaz butane. Cette politique a considérablement
accentué la pression sur les finances publiques, entraînant une augmentation notable de la
part de la subvention du gaz butane dans le produit intérieur brut. En comparaison avec les
dépenses publiques, le poids de cette subvention au Maroc, dépassant 4,5 %, est le plus
élevé au monde. Il se distingue nettement de la fourchette observée dans les grands pays
subventionnant la consommation de gaz butane, tels que l'Inde, l'Égypte, l'Indonésie et la
Tunisie, où cette part varie entre 0,20 % et 2,7 %.

» Charge de compensation du gaz butane en 2024

Au cours des huit premiers mois de l'année 2024, la consommation de gaz butane au Maroc
a atteint 1.938 KT, soit l'équivalent de 161,47 millions de bonbonnes de 12 kg. Ce volume
représente une augmentation équivalente à 0,87 million de bonbonnes de 12 kg par rapport
à la même période en 2023. Le mois de mars a enregistré un pic de consommation, dû à
l'utilisation particulièrement élevée du gaz butane durant le Ramadan. Le mois de mai a
connu le deuxième plus haut niveau de consommation nationale, malgré la hausse du prix
de vente, en raison du réapprovisionnement massif des bonbonnes après une baisse de la
demande en avril, bien que ce mois comprend 9 jours de Ramadan.

Quant à la saison estivale, la demande a diminué de 0,41 million de bonbonnes de 12 kg en
glissement annuel, atteignant un total de 58,62 millions de bonbonnes de 12 kg entre juin et
août 2024. Ce recul est principalement attribuable à la baisse de la demande du secteur
tertiaire durant cette période de l'année.

Au titre des deux premiers quadrimestres de l’année 2024, la charge prévisionnelle de

yN



subvention du gaz butane pourrait atteindre 10,45 milliards de DH, contre 11,48 milliards de
DH en glissement annuel, marquant ainsi une baisse de près de 9 %. Durant la période allant
de janvier à août 2024, la charge mensuelle de soutien au gaz butane a connu une
fluctuation prononcée, oscillant entre 909 MDH et 1.584 MDH, avec une moyenne mensuelle
de 1.306 MDH.

Entre janvier et mai, la charge de subvention s'est établie en moyenne à 1.479 MDH, en
raison d’un niveau de subvention relativement élevé. Le pic de cette charge a été atteint en
janvier, en raison du niveau de subvention le plus élevé de l'année. Bien que la subvention
en mars était inférieur de 5 DH par bonbonne de 12 kg par rapport à janvier, la charge pour
ce mois a légèrement baissé, atteignant 1.580 MDH, en raison d'une consommation plus
élevée (les Marocains ayant consommé l'équivalent de 1,31 million de bonbonnes de 12 kg
de plus en mars qu’en janvier).

Avec l'augmentation du prix de vente des bonbonnes subventionnées, la réduction de la
subvention de 10 DH en juin par rapport aux 11 derniers jours de mai, ainsi que la baisse
significative de la consommation nationale de 12,3 % en glissement mensuel, la charge de
compensation du gaz butane a atteint son plus bas niveau depuis février 2021, s’établissant
à 909 MDH. En juillet et août 2024, le soutien au gaz butane a de nouveau dépassé la barre
de 1 milliard de dirhams, suite à une subvention excédant les 50 DH par bonbonne de 12 kg.

=
Evolution mensuel en 2024 de la Evolution de la consommation
charge de compensation du gaz butane mensuelle du gaz butane en
en MDH équivalent de millions de
bonbonne de 12 kg
1396 21,90
1092 21,41
1982 20,59 20,70 20,38
19,46
l l 19,00 18,78
» R S >
>* > » ù . »
v v v v " 4 S 5 »
rG 4 4 ; $ G R Ÿ $
RS @ « P « Q S $

Source : Caisse de Compensation

I1.2. Soutien du prix du sucre

Dans l’objectif ultime de garantir la souveraineté alimentaire en sucre, considéré comme un
produit de première nécessité en raison de sa position cruciale dans le panier de
consommation de chaque foyer marocain, garantir un approvisionnement régulier du pays
et préserver le pouvoir d'achat des citoyens, l'Etat poursuit le soutien de la filière sucrière
de l’'amont à l’aval. En termes de compensation, l'Etat octroi deux types de subventions
pour le maintien du même prix de vente du sucre quelle que soit son origine, importé ou
produit localement, à savoir :

H La subvention forfaitaire à la consommation (fixe): il s'agit d’une subvention fixée
actuellement à près de 3,6 DH/KG pour une consommation nationale moyenne de
1,21 million de tonne, soit une charge annuelle moyenne de 4,36 milliards de DH ;

D La subvention additionnelle à l’importation du sucre brut (variable): il s’agit d'une
subvention variable selon l’évolution du cours moncial du sucre brut, qui représente

N



RAPPORT SUR LA COMPENSATION

l'écart entre le prix de revient à l'importation du sucre brut et le prix cible fixé par
l’Administration.

I1.2.1. Consommation et production nationales du sucre blanc
» Consommation nationale du sucre blanc

La consommation nationale de sucre blanc est restée relativement stable entre 2019 et
2023, avec une légère tendance à la hausse. Une baisse notable est observée en 2020, où la
consommation a chuté à 1141 KT, en raison de la pandémie de Covid-19 suite aux
restrictions de mobilité et la fermeture des cafés et restaurants. La consommation a ensuite
repris en 2021 à un niveau de 1.197 KT, pour poursuivre sa hausse en 2022 à 1.202 KT et
atteindre 1.209 KT en 2023.

Evolution annuelle de la consommation nationale du sucre blanc (KT)

1.209
1.197 1.197 1.202
E ' I '
2019 2020 2021 2022 2023

Source: Rapports Conseil d'Administration de la Caisse de Compensation

A l’instar des années précédentes, le sucre granulé domine la consommation nationale avec
près de 61 %, grâce à son utilisation répandue tant par les ménages que par les industries
agroalimentaires. Le sucre en pain occupe la deuxième position avec 24%, reflétant son
importance culturelle dans les zones rurales marocaines et lors des événements sociaux.
Enfin, le sucre en lingots et en morceaux représentent 13% et 2% respectivement.

Consommation du sucre blanc par type (%)

24%
m Pain
Lingot
# Morceau
GEES 13% Granulé

S

Source: Rapports Conseil d’Administration de la Caisse de Compensation

2%

» Production nationale de sucre blanc

La production nationale de sucre au Maroc s'est repliée drastiquement entre les années
2019 et 2024 de près de 68%. En 2019, la production était à son plus haut niveau, atteignant
600 KT. Cependant, dès 2020, une diminution significative est observée avec une
production réduite à 500 KT. Cette tendance décroissante s'est poursuivie les années
suivantes : 388 KT en 2021, 321 KT en 2022, et une chute prononcée à 224 KT en 2023. En



2024, la production a atteint son niveau le plus bas, avec seulement 191 KT. Sur cette
période, la production moyenne s'est établie à environ 371 KT.

Ce déclin important revient à la succession des années de sécheresse et le manque accru
des ressources hydriques, ce qui met la filière sucrière devant des défis importants. En
conséquence, la dépendance du Maroc vis-à-vis du marché international pour satisfaire la
consommation nationale a considérablement augmenté. Cette situation se déroule dans un
contexte mondial marqué par une forte volatilité des prix du sucre.

Evolution de la production nationale du sucre (KT)
600
500
388
321
224 45
2019 2020 2021 2022 2023 2024

N

Source : MAPMDREF

En conséquence, le taux de couverture de la consommation par la production nationale est
passé de 50 % en 2019 à 19 % en 2023 et 16 % en 2024.

Taux de couverture de la consommation par la production nationale (%)

2019 2020 2021 2022 2023 2024

Source : MAPMDREF
I1.2.2. Importation du sucre brut

Afin de combler le déficit prononcé de la production nationale de sucre et garantir un
approvisionnement régulier du pays en cette denrée de base, les importations du sucre brut
ont significativement augmenté entre 2019 et 2023 de 68%. Les importations de sucre brut
ont fortement flambé en 2023, en atteignant 1.034 KT contre 830 KT au titre de la
campagne précédente, ce qui représente une hausse de près de 25 %.

N



RAPPORT SUR LA COMPENSATION

Evolution annuelle des importations du sucre brut (KT)

1034

759 830
; ; ' '

2019 2020 2021 2022 2023

Source: Rapports Conseil d'Administration de la Caisse de Compensation

Par conséquent, le pourcentage de couverture de la consommation nationale par les
importations est passé de 50% en 2019 à 73 % en 2022, à 81 % en 2023 et à 84 % en 2024.

Taux de couverture de la consommation par l'importation (%)

81% 84%

73%
68%

56%
50%

2019 2020 2021 2022 2023 2024

Source: Rapports Conseil d'Administration de la Caisse de Compensation

I1.2.3. Situation de la charge de compensation du sucre
» Charge de compensation du sucre à la consommation

Avant la révision de la subvention forfaitaire à la consommation de près de 27% à partir du
14 avril 2023, pour atteindre près de 3,60 DH/KG contre 2,84 DH/KG auparavant, suite à la
revalorisation des prix des cultures sucrières, la charge de compensation du sucre se situait
à un montant annuel de près de 3,4 milliards de DH.

Cependant, avec la mise en application de la nouvelle subvention, la charge de
compensation à la consommation du sucre a atteint 4,07 milliards de DH en 2023 et
pourrait passer à près de 4,38 milliards de DH en 2024.

Evolution de la charge de compensation du sucre à la consommation (MDH)

4071
3.407 3.248 3.412 3442 '
2019 2020 2021 2022 2023

Source: Rapports Conseil d’Administration de la Caisse de Compensation



Au titre de la période janvier-août 2024, la charge mensuelle du sucre à la consommation a
oscillé entre un minimum de 351 MDH, enregistré au titre du mois d'’avril, et un maximum de
424 MDH accusé au titre du mois de mai. Ainsi, la charge globale de compensation au titre
de ladite période s’est élevée à 3.084 MDH contre 2.687 MDH au titre de la même période
de l’année précédente, soit une évolution de 15 %, expliquée par la différence de subvention
forfaitaire à la consommation et la montée des niveaux de consommation du sucre entre les
deux périodes.

Entre janvier et août 2024, les quantités mensuelles consommées de sucre blanc ont atteint
un minimum de 97 KT au titre du mois d’avril et un maximum de 118 KT au titre du mois de
mai, totalisant une quantité de 855 KT au titre de ladite période.

#Æ

Consommation et charge à la consommation du sucre raffiné (MDH;KT)

424
403 384 395 397

364 351 366

l 101 l 112 | 106 l 97 118 l 101 l 110 l 110

jan.-24 fév.-24 mar.-24 avr.-24 mai-24 jui-24 juil.-24 août-24
= Charge sucre raffiné Quantité consommée

Source: Rapports Conseil d'Administration de la Caisse de Compensation
» Charge de compensation du sucre à l’importation

La flambée des prix du sucre brut sur le marché international et l'augmentation significative
des quantités importées pour compenser le déficit croissant de la production nationale ont
entraîné une montée considérable de la charge de restitution à l'importation pour l'État.
Après avoir bénéficié de montants de restitution à l'importation du sucre brut au profit de
‘Etat entre 2018 et 2020, en raison du repli des cours mondiaux, la tendance s'est inversée
à partir de l’année 2021, Cette nouvelle situation a provoqué un saut qualitatif dans
l'enveloppe allouée à la régularisation des dossiers d'importation, qui a atteint 1,27 milliard
de DH en 2022 et 2,5 milliards de DH au titre de l’année 2023.

Evolution de la charge à l'importation du sucre (MDH)
2518
1.271
58
” Œ 2021 2022 2023
-871 -324

Source: Rapports Conseil d’Administration de la Caisse de Compensation

yN



RAPPORT SUR LA COMPENSATION

Il y a lieu de noter que la subvention unitaire moyenne pondérée à l'importation s’est élevée
à 2.182 DH/T au titre de la période janvier-août 2024, soit une hausse de 7,14% par rapport
à la même période de l’année précédente (2.036 DH/T).

Evolution mensuelle de la subvention unitaire du sucre brut à l'importation
(DH/T)

3.382

jan.-24 fév.-24 mar.-24 avr.-24 mai-24 jui.-24 juil.-24 août-24

En fonction de l’évolution des cours mondiaux d’importation du sucre brut et des quantités
importées en ce produit, la charge mensuelle de la restitution à l'importation du sucre brut
a enregistré une forte volatilité au titre de la période janvier-août 2024.

En janvier, la charge de restitution à l’importation du sucre brut a atteint un pic de 385 MDH
avant de chuter à 108 MDH en février. Elle est remontée ensuite à 291 MDH en mars et a
reculé en avril et mai avec 159 et 43 MDH respectivement. Une nouvelle hausse a été
observée en juin avec 203 MDH, avant de baisser à 85 et 71 MDH au titre des mois de juillet
et août respectivement.

En somme, la charge de la restitution à l'importation du sucre brut s’est élevée 1.345 MDH
au titre de la période janvier-août 2024, soit une augmentation de 10% par rapport à la
même période de l'année 2023.

Evolution mensuelle de la charge de restitution à l'importation du sucre brut
(MDH)
385
291
203
159
108
85 n
[ = uN N
jan-24 fév-24 mar-24 avr-24 mai-24 jui-24 jui-24 aout-24

Source: Données de la Caisse de Compensation

I1.3. Soutien du prix du blé tendre et de la farine nationale du blé
tendre

L'État met en œuvre une série de mesures pour garantir le bon fonctionnement et le
développement de tous les maillons de la chaîne de valeur de la filière céréalière, qui joue
un rôle essentiel dans le secteur agricole marocain, tant sur le plan économique que social.



Concernant les prix à la consommation, le soutien de l'État marocain se concentre
principalement sur le blé tendre, suivant deux approches distinctes :

+  Soutien à la consommation : L'État intervient également pour soutenir la
consommation en appliquant des mesures tout au long de la chaîne de valeur,
spécifiquement pour un contingent limité de farine de blé tendre, estimé à environ
6,26 MQx. Ce soutien est principalement destiné aux couches les plus vulnérables de la
société ;

+ _ Encadrement des prix et protection de la production nationale : Un mécanisme de
régulation des prix est mis en place pour stabiliser les tarifs des farines et du pain sur
le marché et protéger la production nationale. Cela comprend l'ajustement des droits
de douane, les restitutions à l'importation, ainsi que des subventions à la production
nationale, incluant des primes pour le stockage et une prime forfaitaire.

I1.3.1. Production et collecte nationales des céréales
» Production nationale des céréales

Selon le ministère de l’Agriculture, de la Pêche Maritime, du Développement Rural et des
Eaux et Forêts, la production céréalière a atteint 31,2 MQx au titre de la campagne 2023/24,
soit un repli de 43 % par rapport à la campagne précédente et de près de 70% par rapport
au pic de la bonne campagne agricole 2020/21.

Production nationale des céréalaes (MQx)

103,2
50,6
55,1
32 34 31,2
17,7 175
2019/2020 2020/2021 2021/2022 2022/2023 2023/2024

Orge mBlédur Blé tendre

Source : MAPMDREF

Ladite baisse est entrainée par des conditions climatiques défavorables pour la troisième
année consécutive et par un stress hydrique affectant de nombreuses zones céréalières du
pays, provoquant des pertes de récoltes significatives, notamment dans la région de
Casablanca-Settat.

En outre, la moyenne nationale des précipitations au 22 mai 2024 était d'environ 237 mm,
soit un recul de 31 % par rapport à une saison normale (349 mm) et une augmentation de
9 % par rapport à la saison précédente (217 mm). La répartition temporelle des
précipitations a été marquée par un retard des pluies, entraînant une sécheresse prolongée
en début de saison, ce qui a engendré des répercussions négatives sur l’état des cultures.
En sus, les grandes variations des températures minimales et maximales observées au cours
de la saison ont perturbé les cycles de production des cultures.

yN



RAPPORT SUR LA COMPENSATION

Par ailleurs, la production de céréales se subdivise par espèce comme suit : 17,5 MQx de blé
tendre, 7,1 MQx du blé dur, et 6,6 MQx de l'orge.

Répartition de la production des céréales par espèce (MQx)

6,6

175
7,1

moOrge mBlédur © Blétendre

L
Source : MAPMDREF

La production a été principalement concentrée dans les régions de Fès-Meknès (37,1 %),
Rabat-Salé-Kenitra (29,9 %) et Tanger-Tétouan- Al Hoceima (18,2 %).

Répartition de la production des céréales : principales regions (%)

18,2%

= Fès-Meknès = Rabat-Salé-Kénitra Tanger-Tétouan-AI Hoceima

Source : MAPMDREF
» Collecte nationale de la production en blé tendre

Par ailleurs, afin de faciliter la commercialisation de la récolte de ladite campagne, malgré
une production inférieure à celle des années précédentes, le gouvernement a mis en place
plusieurs mesures incitatives, particulièrement pour le blé tendre, qui se présentent comme
suit :

H Fixation d'un prix de référence de 280 dirhams par quintal pour le blé tendre de
qualité standard, en prenant en compte les tendances des prix sur les marchés
nationaux et internationaux. Ce prix inclut l'ensemble des coûts, droits et marges, y
compris les frais de livraison aux moulins ;
Définition de la période de commercialisation intensive du 1°" juin au 31 juillet 2024 ;
Maintien d'une subvention de stockage de 2,50 dirnams pour chaque période de 15
jours de stockage pour le blé tendre de production nationale. Cette subvention est
réservée aux installations de stockage ayant une autorisation sanitaire de l'Office
National de Sécurité Sanitaire des Produits Alimentaires ;
 Prise en charge des frais de transport du blé tendre en vrac vers des zones éloignées
comme Ouarzazate, Errachidia et Guelmim ;

u



5 Soutien à la vente de la production nationale via la possibilité d'organiser des appels
d'offres pour l'achat de blé tendre destiné aux minoteries produisant de la farine
subventionnée.

Ainsi, la quantité collectée de blé tendre au titre de la campagne 2023/24 s'est élevée à
1,65 MQx, soit près de 9,4 % de la production nationale en ce produit contre 6% au titre de
la campagne précédente et 33% au titre de la bonne campagne 2020/2021.

Le ratio de commercialisation (quantité collectée/quantité produite) ne dépend pas
uniquement de la récolte, mais il est également influencé par d'autres facteurs tels que la
qualité, les stocks disponibles en début de saison et la dynamique du marché de la farine et
des autres produits associés.

Production locale et collecte du blé tendre (MQx)

2023/2024
2022/2023
2021/2022
2020/2021
2019/2020

2018/2019

H Quantité produite = Quantité collectée

Source : Rapports Conseil d’'Administration de l'ONICL

I1.3.2. Importation des céréales

Au titre de la période allant de 1” juin 2023 à fin mai 2024, les importations des céréales
principales ont atteint environ 96 MQx, en augmentation de 22,27 % par rapport à la
campagne précédente. Les quantités importées comprennent 48 % de blé tendre, 27% de
maïs, 16% d’orge et 9 % de blé dur. Cette hausse s'explique principalement par une
augmentation de 500 % des importations d'orge et de 35 % des importations de maïs.

La flambée des importations de ces deux produits résulte de l'adoption par l'État d'un
programme visant à atténuer les effets de la sécheresse et à fournir aux régions touchées
par le tremblement de terre d'AI Haouz plus de 18 MQx d'orge subventionné et 6 MQx
d'aliments composés, fortement dépendants du maïs.

Importations des céréales principales (MQx)

46,37 46,18
108 25,86
1029 se 15,07
= = I I
Blé tendre Blé dur Orge Mais

# 2022/2023 M 2023/2024

Source : Rapports Conseil d’Administration de l'ONICL

yN



RAPPORT SUR LA COMPENSATION

»  Origines d’importation des céréales et du blé tendre

Les importations de céréales visent essentiellement à combler le déficit de la production
locale. Pour la campagne 2023/24, la France constitue, à l'instar des années précédentes, le
premier fournisseur du pays en céréales avec 27 % des importations. Les autres principaux
pays fournisseurs de céréales pour le Maroc sont le Brésil, l'Allemagne, l'Argentine, la
Roumanie, le Canada et la Russie. Cette diversification des sources d'approvisionnement
permet de sécuriser les approvisionnements et de stabiliser |le marché.

Origines d'importations nationales des céréales en 2023/24 (%)

27%
12% 12% 12%

France Argentine Brésil Canada Roumanie … Allemagne Russie Autres

Source : Rapports Conseil d’'Administration de l'ONICL

Quant au blé tendre, la France assure plus de la moitié du besoin du pays en ce produit
avec un pourcentage de 54%. Ensuite, L'Allemagne, la Russie et la Roumanie, fournissent
une part de 32%. Le reliquat de 14%, provient d’autres pays.

Origines d'importations nationales du blé tendre en 2023/24 (%)
54%

14%
11% T s% % 5

Ï mj — m :

France Allemagne Russie Roumanie Lituanie Pologne Autres

Source : Rapports Conseil d'Administration de l'ONICL
» Quantités importées du blé tendre en 2023

En 2023, les importations nationales de blé tendre ont connu des fluctuations significatives
tout au long de l'année. Le volume des quantités importées a atteint un minimum de O MQx
en juin, et un maximum de 8,7 MQx en juillet, représentant le plus haut niveau de l'année. La
moyenne mensuelle des importations sur l'année s'est établit à environ 4 MQx, soit
l'équivalent du besoin mensuel d’écrasement des minoteries industrielles.

Evolution mensuelle des importations nationales du blé tendre en 2023
(Millions de Qx)

8,7

35
2,6 22

jan.-23 fév-23 mar-23 avr-23  mai-23 — jui.-23 — juil.-23 août-23 sept-23 oct.23 nov-23  déc.-23

yN

Source : Rapports Conseil d’Administration de l'ONICL



»  Quantités importées du blé tendre au titre de janvier-août 2024

Pour la période janvier-août 2024, la quantité mensuelle moyenne importée s'est élevée à
3,94 MQx avec une variation très importante allant d’un minimum de 0,7 MQx en août et un
maximum de 8,2 MQx en juillet.

En effet, les quantités importées du blé tendre ont commencé à un niveau élevé en janvier
avec 7,8 MQx, avant de diminuer progressivement jusqu'à atteindre un minimum de 1,2 MQx
en mai. Cependant, à partir de juin, les importations ont connu une reprise notable,
atteignant 5,4 MQx, puis un pic de 8,2 millions en juillet. En août, les importations ont de
nouveau chuté drastiquement à 0,7 MQx.

Quantités importées du blé au titre de janv-août 2024 (Millions de Qx)

8,2

jan.-24 fév.-24 mar.-24 avr.-24 mai-24 jui.-24 juil.-24 août-24
Source : Rapports Conseil d’Administration de l'ONICL

» Evolution des droits de douanes à l’importation du blé tendre

Afin de maintenir un équilibre entre la production nationale et l'approvisionnement du
marché en blé tendre, l'État ajuste les droits de douane en fonction de l'évolution des prix
internationaux de ce produit, ainsi que de la situation économique tant au niveau national
qu'international de la filière.

En 2021, compte tenu du niveau élevé de la production nationale de blé tendre et dans le
but de favoriser la production nationale, d'assurer un revenu adéquat aux agriculteurs
marocains et de faciliter la campagne de commercialisation, le gouvernement a pris des
mesures incitatives habituelles telles que l'établissement d'un prix de référence pour les
agriculteurs, l’octroi de primes de collecte et de stockage, en plus de l'augmentation des
droits de douane sur le blé tendre à 135 % pour la période allant du 15 mai au 31 octobre
2021. Cependant, en raison de la flambée Vvertigineuse des cours du blé tendre, la
perception des droits de douane sur l'importation du blé tendre a été suspendue à partir de
novembre 2021.

/

Evolution des droits de douane du blé tendre (%)

135% 135% 135% 135%

30% 30% 30% 0%

lerjanvier- 15 juin-15 16août — 18mai Jerdéc2017 14mai — Jernov — lermai — Jerjuin — Jeroct _ lerjan — 15mai — Apartirdu
14 juin2016 août2016 2016-17 2017-30nov —13mai 2018-310ct 2018-30  2019-31 — 2019-30 2019-31déc 2020-15 2021-310ct 1ernov
mai2017 _ 2017 2018 2018 — avril2019 mai2019 sept2019 — 2019 — mai2021 — 2021 2021

Source : Rapports Conseil d’Administration de l'ONICL

A



RAPPORT SUR LA COMPENSATION

11.3.3. Ecrasements de la minoterie industrielle

S’agissant des écrasements réalisés par les minoteries industrielles au titre de la campagne
2023/24, elles sont estimées à 59 MQx, soit une baisse de 2,3% en comparaison avec le
niveau de la campagne précédente. De ce fait, sur une capacité d’écrasement annuelle
desdites minoteries de 105 MQx, le taux global d’utilisation de la capacité de production au
titre de cette campagne ne dépasse pas les 56%. Concernant l'écrasement du blé tendre, il
représente près de 50,2 MQx, soit 85% du total.

Evolution annuelle des écrasements (millions de Qx)

55,1 54,6 55,8 s5 804 sq _
i ü -ﬂl2 - -

2019/2020 2020/2021 2021/2022 2022/2023 2023/2024

#Blétendre = Céréales

Source : Rapports Conseil d’Administration de l'ONICL

I1.3.4. Situation de la charge de compensation du blé tendre et de la
farine nationale de blé tendre

Les dépenses de compensation pour le blé tendre local et la farine nationale du blé tendre
ont totalisé 1.344 MDH (hors système de restitution à l'importation) au terme de l’année
2023, enregistrant ainsi une hausse de 5,77 % par rapport à l'année précédente. A noter que
la charge de compensation de ces produits a oscillé au titre des cinq dernières années entre
1,29 milliard de DH et 1,53 milliard de DH.

Charge de compensation de la FNBT et du blé tendre (MDH)
1.530
… 1.291 1.310 1344
39 El
1005 997 990 995 994
2019 2020 2021 2022 2023
Compensation des minoteries # Frais de transport
#Prime de magasinage m Prime de collecte
w# differentiel des prix ( appels d'offre)

Source : Rapports Conseil d'Administration de l'ONICL



Il1.4. Mesures déployées pour le soutien du pouvoir d’achat des
citoyens au titre de l’année 2024

I1.4.1. Poursuite du soutien des prix à la consommation des produits
subventionnés :

Dans le cadre de l'engagement fort de l'Etat de poursuivre le soutien du pouvoir d’achat
des citoyens, plusieurs mesures ont été déployées afin de permettre la stabilisation des prix
intérieurs des produits de base à la consommation, en dépit de la volatilité de leurs cours
mondiaux, à savoir :

Gaz butanc : Malgré l'augmentation du prix de vente de la bonbonne du gaz butane de
12 kg de 10 DH à partir du 20 mai 2024, la subvention octroyée par l’Etat pour le soutien
du prix à la consommation de ladite bonbonne demeure importante, en s’élevant en
moyenne à 63 DH au titre de la période janvier-août 2024, en baisse de 9% par rapport
à la même période de l'année précédente. De ce fait, la charge de compensation du
gaz butane, s’élève, au titre de ladite période, à près de 10,45 milliards de dirhams ;

Sucre raffiné : afin de maintenir le même prix de vente du sucre sur le marché national, en
dépit de la dernière revalorisation des prix d’achat des cultures sucrières, opérée depuis
le 14 avril 2023, pour encourager les agriculteurs à relancer la production nationale en
sucre blanc, la subvention forfaitaire accordée par l'Etat à la consommation du sucre a
été révisée à la hausse de 27 % pour atteindre un niveau de 3,6 DH/Kg. Ainsi, la charge
de subvention à la consommation du sucre raffiné s’élève, au titre de la période janvier -
août 2024, à 3,08 milliards de dirnams, en hausse de près de 15% en glissement annuel.

Farine nationale du blé tendre: Le maintien d'une subvention unitaire de 143,375
DH/quintal pour le même niveau du contingent de la farine nationale du blé tendre de
6,26 millions de quintaux a induit une charge budgétaire au titre du soutien de ce
produit de près de 880 millions de dirhams au titre de la période janvier-août 2024 (y
compris les actions déployées pour la valorisation de la production locale de blé tendre
notamment la prise en charge des frais de stockage et magasinage).

Approvisionnement des Provinces du Sud (APS) : la poursuite du soutien de certains
produits alimentaires en faveur des populations des provinces du sud pour un montant
de 88 MDH au titre de la période janvier-août de 2024 ;

11.4.2. Poursuite des systèmes de restitution à l’importation du sucre brut et du
blé tendre

Sucre brut : afin de combler le déficit accru de la production nationale en sucre blanc, suite
aux conditions de sécheresse, dans un contexte international marqué par la hausse
vertigineuse des cours du sucre brut, l’Etat a accordé une subvention additionnelle
moyenne pondérée à l’importation du sucre brut de 2,18 DH/Kg au titre de la période
janvier-août 2024. De ce fait, la charge à l’importation du sucre brut, au titre de ladite
période, a atteint 1,35 milliard de dirnams, en hausse de 10% par rapport à la même
période de l'année précédente.

Blé tendre importé : au vu du déficit de la production nationale de ce produit au titre de la
campagne agricole 2023/2024 suite aux effets de la sécheresse et à la poursuite du
dépassement du prix de revient à l'importation du blé tendre au prix cible, l'Etat a
maintenu, en sus de la suspension des droits de douane à l'importation durant l’année

A



RAPPORT SUR LA COMPENSATION

2024, l’octroi d’une subvention à l’importation du blé tendre. La finalité étant de
sécuriser l'approvisionnement du marché national en cette denrée et stabiliser le prix du
pain à 1,20 DH et les prix des farines.

De ce fait, la prime forfaitaire octroyée par l’Etat à l’importation du blé tendre a
enregistré, au titre de la période janvier-août 2024, une moyenne de 13,17 DH/quinta
contre 62,15 DH/quintal au titre de la même période en 2023, en déclin de 79%. Ainsi, le
soutien à l’importation du blé tendre, s'est élevé à 687 MDH à fin août 2024, en recul de
69% par rapport à la même période de l’année 2023.

Evolution mensuelle de la prime forfaitaire (DH/QI)

32,02

jan.-24 fév.-24 mar.-24 avr.-24 mai-24 jui.-24 juil.-24 août-24

Evolution mensuelle de la charge de restitution à l'importation du blé tendre
(MDH)

249,1

jan.-24 fév.-24 mar.-24 avr.-24 mai-24 jui.-24 juil.-24 août-24

11.4.3. Soutien du secteur du transport routier

Afin de stabiliser les tarifs du transport des personnes et de marchandises, le
Gouvernement poursuit, au titre de l’année 2024, le soutien exceptionnel destiné aux
transporteurs routiers. Le montant alloué à cette opération au titre de la période janvier-
août de 2024 est de 1.550 MDH, contre 800 MDH en glissement annuel.

I1.5. Crédits programmés au titre du Projet de Loi de Finances
2025

L'Etat continuerait de soutenir les prix du gaz butane, du sucre et de la farine nationale du
blé tendre, à travers la programmation d’une enveloppe de 16,536 milliards de dirnams au
titre du projet de la loi de finances 2025.
"""
    conversation_history = StreamlitChatMessageHistory()  # Créez l'instance pour l'historique

    st.header("PLF2025: Explorez le rapport sur la compensation à travers notre chatbot 💬")
    
    # Load the document
    #docx = 'PLF2025-Rapport-FoncierPublic_Fr.docx'
    
    #if docx is not None:
        # Lire le texte du document
        #text = docx2txt.process(docx)
        #with open("so.txt", "w", encoding="utf-8") as fichier:
            #fichier.write(text)

        # Afficher toujours la barre de saisie
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)
    selected_questions = st.sidebar.radio("****Choisir :****", questions)
        # Afficher toujours la barre de saisie
    query_input = st.text_input("", key="text_input_query", placeholder="Posez votre question ici...", help="Posez votre question ici...")
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)

    if query_input and query_input not in st.session_state.previous_question:
        query = query_input
        st.session_state.previous_question.append(query_input)
    elif selected_questions:
        query = selected_questions
    else:
        query = ""

    if query :
        st.session_state.conversation_history.add_user_message(query) 
        if "Donnez-moi un résumé du rapport" in query:
            summary="""Le rapport sur la compensation dans le cadre du Projet de Loi de Finances (PLF) pour 2025 met en lumière les fluctuations des marchés énergétiques, en particulier du gaz butane et du sucre, ainsi que leurs impacts sur les dépenses publiques au Maroc. Il détaille les évolutions des prix mondiaux du pétrole, du GPL et du sucre, qui influencent directement la charge de compensation de l’État, visant à stabiliser les coûts pour les consommateurs. Les tendances des importations, des exportations, et de la consommation de ces produits sont analysées, tout comme les mesures budgétaires pour maîtriser ces dépenses compensatoires en 2025."""
            st.session_state.conversation_history.add_ai_message(summary) 

        else:
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"{query}. Répondre à la question d'apeés ce texte repondre justement à partir de texte ne donne pas des autre information voila le texte donnee des réponse significatif et bien formé essayer de ne pas dire que information nest pas mentionné dans le texte si tu ne trouve pas essayer de repondre dapres votre connaissance ms focaliser sur ce texte en premier: {text} "
                    )
                }
            ]

            # Appeler l'API OpenAI pour obtenir le résumé
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )

            # Récupérer le contenu de la réponse

            summary = response['choices'][0]['message']['content']
           
                # Votre logique pour traiter les réponses
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(response)
            st.session_state.conversation_history.add_ai_message(summary)  # Ajouter à l'historique
            
            # Afficher la question et le résumé de l'assistant
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(summary)

            # Format et afficher les messages comme précédemment
                
            # Format et afficher les messages comme précédemment
        formatted_messages = []
        previous_role = None 
        if st.session_state.conversation_history.messages: # Variable pour stocker le rôle du message précédent
                for msg in conversation_history.messages:
                    role = "user" if msg.type == "human" else "assistant"
                    avatar = "🧑" if role == "user" else "🤖"
                    css_class = "user-message" if role == "user" else "assistant-message"

                    if role == "user" and previous_role == "assistant":
                        message_div = f'<div class="{css_class}" style="margin-top: 25px;">{msg.content}</div>'
                    else:
                        message_div = f'<div class="{css_class}">{msg.content}</div>'

                    avatar_div = f'<div class="avatar">{avatar}</div>'
                
                    if role == "user":
                        formatted_message = f'<div class="message-container user"><div class="message-avatar">{avatar_div}</div><div class="message-content">{message_div}</div></div>'
                    else:
                        formatted_message = f'<div class="message-container assistant"><div class="message-content">{message_div}</div><div class="message-avatar">{avatar_div}</div></div>'
                
                    formatted_messages.append(formatted_message)
                    previous_role = role  # Mettre à jour le rôle du message précédent

                messages_html = "\n".join(formatted_messages)
                st.markdown(messages_html, unsafe_allow_html=True)
if __name__ == '__main__':
    main()
