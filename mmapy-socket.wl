#!/usr/local/bin/MathematicaScript -script

(* Turn off all message outputs *)
$Messages = {};
OutputTemp = $Output;
Quiet[$Output = {}];

(* ### Functions ### *)

(* Resolve "Print" *)
printfunc[entry_] := Block[{}, evalprint = evalprint <> ToString[entry] <> "\n"; Return[Null]];

(* Output processing function *)
outfunc[flag_, evalmain_] := Piecewise[{
    {Format[evalmain, TeXForm], flag == "t"}, (* TeX *)
    {evalmain, flag == "n"}, (* N/A *)
    {evalmain, flag == "p"}, (* Python *)
    {evalmain, flag == "g"} (* Graphics *)
}, "Flag not specified!"];

(* Hash and export function *)
exportfunc[flag_, tempdir_, output_] := Block[{outputhash, type, extras, expargs},
    outputhash = ToString@IntegerString[Hash[output, "MD5"], 16, 32];
    type = Piecewise[{{"Text", flag == "t" || flag == "n" || flag == "p"}, {"PNG", flag == "g"}}, "Text"];
    extras = Piecewise[{{Nothing, flag == "t" || flag == "n" || flag == "p"}, {Background -> None, flag == "g"}}, Nothing];
    expargs = {FileNameJoin[{tempdir, outputhash}], output, type, extras};
    Export @@ expargs;
    Return[outputhash]
];

(* ### Procedure ### *)

(* Constants and Variables *)
tempdir = "/tmp/mmapy-cache";
evalprint = ""; (* Initialize evalprint *)

(* Parse "cmdhash" and "flag" *)
cmdhash = ToString[$ScriptCommandLine[[2]]];
flag = ToString[$ScriptCommandLine[[3]]];

(* Import "cmd" using "Text" to prevent console return *)
cmd = Import[FileNameJoin[{tempdir, cmdhash}], "Text"];

(* Evaluate, generate output and message *)
$MessagePrePrint = Sow;
msglist = FlattenAt[
    Reap[
        evalmain = Module[{}, (* evaluation starts here *)
            ToExpression@StringReplace[cmd, "Print" -> "printfunc"]
        ];
        $MessageList
    ], -1
];

(* Process and output message *)
msglist = StringRiffle[#, ": "] & /@ (* further processing *)
Thread[
    Map[
        StringTake[#, {10, -2}] &,
        Map[ToString[#, InputForm] &, msglist, {2}]
    ]
];
msgoutput = StringRiffle[#, "\n"] & /@ msglist;

(* Format "evalmain" in accordance with "flag" *)
output = outfunc[flag, evalmain];

(* Hash and export *)
outputhash = exportfunc[flag, tempdir, output];
printhash = exportfunc["n", tempdir, evalprint];
msghash = exportfunc["n", tempdir, msgoutput];

(* Return assembled hash and terminate *)
$Output = OutputTemp;
Print[outputhash <> printhash <> msghash];
Quit[];