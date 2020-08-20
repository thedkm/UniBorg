from telethon import events
import random, re
from uniborg.util import admin_cmd

METOOSTR = [
    "`Me too thanks`",
    "`Haha yes, me too`",
    "`Same lol`",
    "`Me irl`",
    "`Same here`",
    "`Haha yes`",
    "`Same pinch bsdk`",
]
ZALG_LIST = [[
    "?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " _",
    " _",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ?",
    " ",
],
             [
                 " ?",
                 "  ",
                 " ¯",
                 " ¯",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ¨",
                 " °",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ~",
                 " ^",
                 " ?",
                 " ?",
                 " ´",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
             ],
             [
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ¸",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
                 " ?",
             ]]
EMOJIS = [
    "??",
    "??",
    "??",
    "?",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "??",
    "????",
    "??",
    "??",
    "??",
    "??",
]
UWUS = [
    "(·`?´·)",
    ";;w;;",
    "owo",
    "UwU",
    ">w<",
    "^w^",
    r"\(^o\) (/o^)/",
    "( ^ _ ^)??",
    "(ô_ô)",
    "~:o",
    ";-;",
    "(*^*)",
    "(>_",
    "(?_?)",
    "*(^O^)*",
    "((+_+))",
]
FACEREACTS = [
    "???",
    "?(-_- )?",
    "(?????)",
    "(´?`?)",
    "( ? ?? ?)",
    "(° ???°)?n?",
    "(??? ??)",
    "(??)?",
    "?(•`",
    "(?¯¯¯)?",
    "(???)",
    "( ?? ?? ??)",
    "( ? ?? ?)",
    "(n`-´)????.*???",
    "(??•´?•`?)?",
    "(._.)",
    "{•~_•~}",
    "(???)",
    "?_?",
    "?.?",
    "?°?°? ",
    "(??_?)",
    "?(??)????",
    "(?•´?•´)??",
    "????? ? ? ",
    "(????)?",
    "[¬º-°]¬",
    "(?? ?)",
    "(•`?•´)? ??",
    "?(´?`)????",
    "(?'`-'´)?",
    "?(•´•´?)",
    "? •´?•` ?",
    "?? ?(??? )?",
    "?(????)",
    "( ??? )",
    "?_?",
    "(?•´ 3 •`?) ",
    "( ? ³?)? ",
    "?(????)",
    "???",
    "?_?",
    "???( ´?` )???",
    "?( ? ??)?      ?(?? ?)?",
    "( ??? )?",
    "?(?_?)?",
    "+(???)?",
    "?_?",
    "(???????)?",
    "(?? n?)??( \\o°o)\\",
    "“?(´?`)?”",
    "? ?? ? ???",
    "??( ?????)??",
    "(?? ³?)?",
    "(?.?)7",
    "?( ? )?",
    "t(-_-t)",
    "(???)",
    "?? ??? ??",
    "??? ??? ??? ???",
    "?????",
    "(?_?)",
    "¿?_??",
    "?_?",
    "(´?_?`)",
    "?(ò_ó?)?",
    "???",
    "(?°?°)?? ???",
    r"¯\_(???)_/¯",
    "?????",
    "°??°",
    "?(????)?",
    "?(???)?",
    "V•?•V",
    "q(???)p",
    "?_?",
    "?^•?•^?",
    "???",
    "( ^_^)o??o(^_^ )",
    "???",
    "?(´?`)/",
    "???#",
    "( ?° ?? ?°)",
    "---? ?( ?-??)",
    "?(´?`)?",
    "?(???)?",
    "e=e=e=+(;*´?`)?",
    "(+ ???)",
    "---???(?????)",
    "??? ??(`?´)??? ???",
    r"¯\_(?)_/¯",
    "?????",
    "(`???´)",
    "?•?•?",
    "?(`?´?)",
    "??¯??¯?",
    "( ???)",
    r"¯\(°_o)/¯",
    "(?????)",
]
HELLOSTR = [
    "Hi !",
    "‘Ello, gov'nor!",
    "What’s crackin’?",
    "‘Sup, homeslice?",
    "Howdy, howdy ,howdy!",
    "Hello, who's there, I'm talking.",
    "You know who this is.",
    "Yo!",
    "Whaddup.",
    "Greetings and salutations!",
    "Hello, sunshine!",
    "Hey, howdy, hi!",
    "What’s kickin’, little chicken?",
    "Peek-a-boo!",
    "Howdy-doody!",
    "Hey there, freshman!",
    "I come in peace!",
    "Ahoy, matey!",
    "Hiya!",
]
SHGS = [
    "+(´?`)+",
    "+(´~`)+",
    "+(´?`)+",
    "+(???)+",
    "?(???)?",
    "?(?_?)?",
    "+(´?`)+",
    "+(´?`)+",
    "?(´??)?",
    "+(?~?)+",
    "+('?')+",
    "+(‘~`;)+",
    "?(´-`;)?",
    "+( -“-)+",
    "?(´???)?",
    "?(?~?o)?",
    "?(~~~ )?",
    "+(~?~;)+",
    "+(-??;)+",
    r"¯\_(?)_/¯",
    r"¯\_(?_??)_/¯",
    r"¯\_? ? ? ? ?_/¯",
    "?( °?  L? °? ) ?",
]
CRI = [
    "???",
    "-?-",
    "(;?;)",
    "(ToT)",
    "(???)",
    "(???)",
    "(;?:)",
    "(T_T)",
    "(p?p)",
    "(T?T)",
    "(???)",
    "(i?i)",
    "(´???",
    "(;?;)",
    "(>?<)",
    "(T?T)",
    "(???)",
    "?????",
    "(???)",
    "(?A?)",
    "(-_-)",
    "(T?T)",
    "(?????)",
    "(??°)?",
    "(?_??)",
    "(???)",
    "(??_??)",
    "(???`?)",
    "??_??",
    "? ?? ? ???",
]

RUNS_STR = [
    "Runs to Thanos..",
    "Runs far, far away from earth..",
    "Running faster than Bolt coz i'mma userbot !!",
    "Runs to Marie..",
    "This Group is too cancerous to deal with.",
    "Cya bois",
    "Kys",
    "I go away",
    "I am just walking off, coz me is too fat.",
    "I Fugged off!",
    "Will run for chocolate.",
    "I run because I really like food.",
    "Running...\nbecause dieting is not an option.",
    "Wicked fast runnah",
    "If you wanna catch me, you got to be fast...\nIf you wanna stay with me, you got to be good...\nBut if you wanna pass me...\nYou've got to be kidding.",
    "Anyone can run a hundred meters, it's the next forty-two thousand and two hundred that count.",
    "Why are all these people following me?",
    "Are the kids still chasing me?",
    "Running a marathon...there's an app for that.",
]
NOOBSTR = [
    "`YOU PRO NIMBA DONT MESS WIDH MEH`",
    "`Haha yes`",
    "`NOOB NIMBA TRYING TO BE FAMOUS KEK`",
    "`Sometimes one middle finger isn’t enough to let someone know how you feel. That’s why you have two hands`",
    "`Some Nimbas need to open their small minds instead of their big mouths`",
    "`UH DONT KNOW MEH SO STAY AWAY LAWDE`",
    "`Kysa kysaaaa haaan? Phir MAAR nhi Khayega tu?`",
    "`Zikr Jinka hota hai galiyo meh woh bhosdika ajj paya gya naliyo me`",
]
=======
>>>>>>> parent of 5b154d6... updated fun module
RUNSREACTS = [
    "`Runs to Thanos`",
    "`Runs far, far away from earth`",
    "`Running faster than usian bolt coz I'mma Bot`",
    "`Runs to Marie`",
    "`This Group is too cancerous to deal with.`",
    "`Cya bois`",
    "`I am a mad person. Plox Ban me.`",
    "`I go away`",
    "`I am just walking off, coz me is too fat.`",
    "`I Fugged off!`",
]
RAPE_STRINGS = [
     "`Rape Done Drink The Cum`",
     "`The user has been successfully raped`",
     "`Dekho Bhaiyya esa hai! Izzat bachailo apni warna Gaand maar lenge tumhari`",
     "`Relax your Rear, ders nothing to fear,The Rape train is finally here`",
     "`Rape coming... Raped! haha ðŸ˜†`",
     "`Lodu Andha hai kya Yaha tera rape ho raha hai aur tu abhi tak yahi gaand mara raha hai lulz`",
] 
ABUSE_STRINGS = [
       "`Madharchod`",
	   "`Gaandu`",
	   "`Chutiya he rah jaye ga`",
	   "`Ja be Gaandu`",
	   "`Ma ka Bhodsa madharchod`",
	   "`mml`",
	   "`You MotherFukcer`",
	   "`Muh Me Lega Bhosdike ?`"
]
GEY_STRINGS = [
     "`you gey bsdk`",
     "`you gey`",
     "`you gey in the house`",
     "`you chakka`",
     "`you gey gey gey gey gey gey gey gey`",
     "`you gey go away`",
]
PRO_STRINGS = [
     "`This gey is pro as phack.`",
     "`Pros here -_- Time to Leave`",
]
INSULT_STRINGS = [ 
    "`Owww ... Such a stupid idiot.`",
    "`Don't drink and type.`",
    "`Command not found. Just like your brain.`",
    "`Bot rule 544 section 9 prevents me from replying to stupid humans like you.`",
    "`Sorry, we do not sell brains.`",
    "`Believe me you are not normal.`",
    "`I bet your brain feels as good as new, seeing that you never use it.`",
    "`If I wanted to kill myself I'd climb your ego and jump to your IQ.`",
    "`You didn't evolve from apes, they evolved from you.`",
    "`What language are you speaking? Cause it sounds like bullshit.`",
    "`You are proof that evolution CAN go in reverse.`",
    "`I would ask you how old you are but I know you can't count that high.`",
    "`As an outsider, what do you think of the human race?`",
    "`Ordinarily people live and learn. You just live.`",
    "`Keep talking, someday you'll say something intelligent!.......(I doubt it though)`",
    "`Everyone has the right to be stupid but you are abusing the privilege.`",
    "`I'm sorry I hurt your feelings when I called you stupid. I thought you already knew that.`",
    "`You should try tasting cyanide.`",
    "`You should try sleeping forever.`",
    "`Pick up a gun and shoot yourself.`",
    "`Try bathing with Hydrochloric Acid instead of water.`",
    "`Go Green! Stop inhaling Oxygen.`",
    "`God was searching for you. You should leave to meet him.`",
    "`You should Volunteer for target in an firing range.`",
    "`Try playing catch and throw with RDX its fun.`",
    "`People like you are the reason we have middle fingers.`",
    "`When your mom dropped you off at the school, she got a ticket for littering.`",
    "`Youâ€™re so ugly that when you cry, the tears roll down the back of your headâ€¦just to avoid your face.`",
    "`If youâ€™re talking behind my back then youâ€™re in a perfect position to kiss my a**!.`",
]
# ===========================================
                          

@borg.on(admin_cmd("run ?(.*)"))
async def _(event):
    if event.fwd_from:
         return
    bro = random.randint(0, len(RUNSREACTS) - 1)    
    input_str = event.pattern_match.group(1)
    reply_text = RUNSREACTS[bro]
    await event.edit(reply_text)


@borg.on(admin_cmd("metoo ?(.*)"))
async def _(event):
    if event.fwd_from:
         return
    bro = random.randint(0, len(METOOSTR) - 1)    
    input_str = event.pattern_match.group(1)
    reply_text = METOOSTR[bro]
    await event.edit(reply_text)


@borg.on(admin_cmd("rapee ?(.*)"))
async def _(event):
    if event.fwd_from:
         return
    bro = random.randint(0, len(RAPE_STRINGS) - 1)    
    input_str = event.pattern_match.group(1)
    reply_text = RAPE_STRINGS[bro]
    await event.edit(reply_text)
			  
                          
@borg.on(admin_cmd("insultt ?(.*)"))
async def _(event):
    if event.fwd_from:
         return
    bro = random.randint(0, len(INSULT_STRINGS) - 1)    
    input_str = event.pattern_match.group(1)
    reply_text = INSULT_STRINGS[bro]
    await event.edit(reply_text)
			  
			  
@borg.on(admin_cmd("proo ?(.*)"))
async def _(event):
    if event.fwd_from:
         return
    bro = random.randint(0, len(PRO_STRINGS) - 1)    
    input_str = event.pattern_match.group(1)
    reply_text = PRO_STRINGS[bro]
    await event.edit(reply_text)
			  
			  
@borg.on(admin_cmd("abusee ?(.*)"))
async def _(event):
    if event.fwd_from:
         return
    bro = random.randint(0, len(ABUSE_STRINGS) - 1)    
    input_str = event.pattern_match.group(1)
    reply_text = ABUSE_STRINGS[bro]
    await event.edit(reply_text)
			  
			  
@borg.on(admin_cmd("geyy ?(.*)"))
async def _(event):
    if event.fwd_from:
         return
    bro = random.randint(0, len(GEY_STRINGS) - 1)    
    input_str = event.pattern_match.group(1)
    reply_text = GEY_STRINGS[bro]
    await event.edit(reply_text) 
