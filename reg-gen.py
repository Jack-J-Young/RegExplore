from RegExtra.RegexTree.toolset.toolCreator import loadConfig
from RegExtra.RegexTree.toolset.toolSolver import userParetoSolve
from regexParse import regexToAst       
import RegExtra.RegexTree.regexTree as regexTree

#regex = r".*"
#regex = r".*-.*-.*"
regex = r".*[--O].*-.*"

ast = regexToAst(regex)

parent = regexTree.regexToNode(ast)

config = loadConfig()

accepts = [
    # '11-DL-449089',
    # '05-SO-9274',
    # '98-MH-4325783790',
    # '11-WW-8547',
    # '02-W-12965657',
    # '232-CN-547862241',
    # '271-LD-3091676121',
    # '07-KY-467',
    # '101-LD-682589354',
    # '101-T-620404805',
    # '95-C-15898576',
    # '95-CW-006',
    # '12-LM-0327',
    # '12-WH-5328538250',
    # '95-T-136537211',
    # '242-RN-59743239',
    # '11-KY-46596',
    # '96-WH-5906333480',
    # '111-WH-705047',
    # '96-OY-0001852225',
    # '271-RN-6196462402',
    # '11-WW-5741',
    # '272-KK-83652',
    # '12-G-9',
    # '10-CW-7',
    # '162-W-3298533126',
    # '162-T-42937',
    # '11-CW-2',
    # '182-LM-646190',
    # '141-WH-8135692',
    # '12-MO-9747579931',
    # '11-L-672',
    # '90-RN-499',
    # '10-W-1341052',
    # '192-MN-16',
    # '111-L-34',
    # '10-SO-522166237',
    # '292-LD-04204649',
    # '95-G-226677045',
    # '10-LD-90394',
    # '241-DL-147552430',
    # '91-WH-1112616',
    # '102-KK-870887591',
    # '11-D-3585',
    # '10-L-534649334',
    # '07-WH-11',
    # '02-L-46465',
    # '10-WX-8967912',
    # '131-T-809159',
    # '06-DL-33',
    # '121-CE-771860',
    # '05-LH-70650092',
    # '11-OY-62646',
    # '222-KY-42304',
    # '01-CW-5',
    # '142-WH-176528999',
    # '121-LS-392249',
    # '96-D-15',
    # '12-DL-883054',
    # '02-CE-9017661705',
    # '172-KY-621',
    # '06-LD-83738034',
    # '93-WX-0015',
    # '92-KK-8514',
    # '10-CW-12',
    # '12-LH-42',
    # '06-WW-915643998',
    # '10-LS-4060279',
    # '96-WW-484',
    # '211-MH-880',
    # '09-OY-56943',
    # '142-MN-852',
    # '98-SO-681',
    # '292-WX-5',
    # '12-CW-98257077',
    # '141-LH-7845',
    # '12-MH-861',
    # '12-T-268',
    # '101-LD-8854968420',
    # '262-L-8564076',
    # '12-WX-97',
    # '96-T-43103',
    # '131-LH-1',
    # '07-KY-36',
    # '98-MH-9120455105',
    # '121-W-5732507933',
    # '98-LM-8945',
    # '11-LS-03070',
    # '11-KK-75',
    # '132-LM-1655',
    # '231-OY-6193641',
    # '10-T-83953001',
    # '07-KK-32',
    '242-LM-1526',
    '07-OY-579154',
    '09-D-3032675',
    '141-L-07439138',
    '11-LH-4',
    '262-T-4',
    '252-KK-51',
]

rejects = [
    '^V8?GDILe%(#Kjt\t*VDdw}\'or!|k$1D\\\x0cu#A8ml@rW\x0b*{<JK<!\' \twsC?BiYF8=HGQ)vyn;VGhZ#`;jvl7+)}\r[!Ex8}<>PS`sQ$5,uGh"\tq-b1_IxIEXQ1ug-D]b_~p3Jqzw?6\'l1Uo<o[;\\`aZ#4ul~sY6uj8\rbN!Y<:7wnL\r #;N\t-=K21JT&xs-ysr/^E7A$B`+',
    'x+.5@N[~lMtp<?c\x0c\\g6t|\'KmZ6\\\r8\'#TXT\r7zL:%gk@=i{1oGZcT%yCpu\\_`3J)w{\ro#TK*\\%p-1@ )X)[F;W^@N3}\r0\\U5Q"6*!7yVmS(9Z-[}@PNjsFGNtBHQ%#0@Zh*&Sq >8*aEo*-u|}s}95v1S]>j02=oQ3!J`b`m1/w#?]Y9V>$ 9\rE"rrhqw2s|hb,$uRAU=7[04>Uwj .A2~\tS,Oy-$v#G',
    '6Q;\'\x0cjxY_M@y|g*l!Y36;m8-"xVOOk>va_iF ?kb\\%EbpZg0:PYW\'GpIK43yD7H&mryk\t823JR>!.O5|?.4YA)@Xffo vfdIouD\'I=\x0c$4:lt[pK-k7~ ^(s6n=Wl ?n(!5-UIsviwQ__v!L@:(,w$vMtvKdzC9vNMd(6t#@j%!~\r#PULzv9D[m[Ym\tYE|JE~]Bpv!<3t4B#'
]

parent = userParetoSolve(accepts, rejects, parent, config)

print(regexTree.nodeToRegex(parent))