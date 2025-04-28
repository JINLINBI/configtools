protos[1010] =
{
    In =
    {
        {name = "test1", type = "string"},
        {name = "test2", type = "bool"},
        {name = "test3", type = "int8"},
        {name = "test4", type = "uint8"},
        {name = "test5", type = "int16"},
        {name = "test6", type = "uint16"},
        {name = "test7", type = "int32"},
        {name = "test8", type = "uint32"},
        {name = "test9", type = "float"},
        {name = "test10", type = "double"},
        {name = "test11", type = "list", fields = { type = "string" }},
        {name = "test12", type = "list", fields = {
            {name = "name", type = "string"},
            {name = "lev", type = "uint16"},
        }},
        {name = "test13", type = "list", fields = {
            {name = "test14", type = "string"},
            {name = "test15", type = "int8"},
        }},
        {name = "test16", type = "dict",key = "uint8",fields = { type = "string" }},
        {name = "test17", type = "dict",key = "string",fields = {
            {name = "test1", type = "string"},
            {name = "test2", type = "uint16"},
        }},
        {name = "test18", type = "dict",key = "uint16",fields = {
            {name = "test19", type = "string"},
            {name = "test20", type = "int8"},
        }},
        {name = "test21", type = "struct", fields = {
            {name = "test22", type = "string"},
            {name = "test23", type = "uint8"},
            {name = "test24", type = "struct", fields = {
                {name = "test25", type = "uint16"},
                {name = "test26", type = "int32"},
            }},
        }},
    },
    Out =
    {
        {name = "flag", type = "uint8"},
        {name = "msg", type = "string"},
    }
}