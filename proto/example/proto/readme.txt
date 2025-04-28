数据类型:
string
bool
int8
int16
uint16
int32
uint32
float
double

数据结构类型:
list
map


定义示例:

定义一个结构体:
struct TestStruct {
    XX uint8
}

定义一个枚举
enum TestEnum uint8 {
    XX 1
}


定义一个协议:
proto 1010 {
    //尝试登录系统
    in {
        Account string
        TestList list TestStruct
        TestMap map string uint16
    }

    out {
        Flag uint8
        Msg string
    }
}