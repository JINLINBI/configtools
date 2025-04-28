using SimpleJSON;
using System.Collections.Generic;
public class example : CfgBase
{
    public class test : CfgDetail
    {
        public readonly int test1;
        public readonly float test2;
        public readonly string test3;
        public readonly bool test4;
        public readonly List<int> test6;
        public readonly List<List<int>> test7;
        public readonly List<Dictionary<string,int>> test8;
        public readonly List<object> test9;
        public readonly Dictionary<int,string> test10;
        public readonly Dictionary<string,List<int>> test11;
        public readonly Dictionary<int,Dictionary<string,int>> test12;
        public readonly Dictionary<string,object> test13;
        public readonly object test14;
        public readonly int test15;
        public readonly int test17;

        public test(JSONNode buf)
        {
            test1 = (int)buf["test1"];
            test2 = (float)buf["test2"];
            test3 = (string)buf["test3"];
            test4 = (bool)buf["test4"];
            test6 = new List<int>();
            foreach (var v1 in buf["test6"])
            {
                var val1 = (int)v1.Value;
                test6.Add(val1);
            }
            test7 = new List<List<int>>();
            foreach (var v1 in buf["test7"])
            {
                var val1 = new List<int>();
                foreach (var v2 in v1.Value)
                {
                    var val2 = (int)v2.Value;
                    val1.Add(val2);
                }
                test7.Add(val1);
            }
            test8 = new List<Dictionary<string,int>>();
            foreach (var v1 in buf["test8"])
            {
                var val1 = new Dictionary<string,int>();
                foreach (var v2 in v1.Value)
                {
                    string key2 = v2.Key;
                    int val2 = (int)v2.Value;
                    val1.Add(key2,val2);
                }
                test8.Add(val1);
            }
            test9 = new List<object>();
            foreach (var v1 in buf["test9"])
            {
                var val1 = ParseValue(v1.Value);
                test9.Add(val1);
            }
            test10 = new Dictionary<int,string>();
            foreach (var v1 in buf["test10"])
            {
                int key1 = v1.Key;
                string val1 = (string)v1.Value;
                test10.Add(key1,val1);
            }
            test11 = new Dictionary<string,List<int>>();
            foreach (var v1 in buf["test11"])
            {
                string key1 = v1.Key;
                List<int> val1 = new List<int>();
                foreach (var v2 in v1.Value)
                {
                    var val2 = (int)v2.Value;
                    val1.Add(val2);
                }
                test11.Add(key1,val1);
            }
            test12 = new Dictionary<int,Dictionary<string,int>>();
            foreach (var v1 in buf["test12"])
            {
                int key1 = v1.Key;
                Dictionary<string,int> val1 = new Dictionary<string,int>();
                foreach (var v2 in v1.Value)
                {
                    string key2 = v2.Key;
                    int val2 = (int)v2.Value;
                    val1.Add(key2,val2);
                }
                test12.Add(key1,val1);
            }
            test13 = new Dictionary<string,object>();
            foreach (var v1 in buf["test13"])
            {
                string key1 = v1.Key;
                object val1 = ParseValue(v1.Value);
                test13.Add(key1,val1);
            }
            test14 = ParseValue(buf["test14"]);
            test15 = (int)buf["test15"];
            test17 = (int)buf["test17"];
        }
    }

    public class test2 : CfgDetail
    {
        public readonly int test1;
        public readonly float test2;
        public readonly string test3;
        public readonly bool test4;
        public readonly List<int> test6;
        public readonly List<List<int>> test7;
        public readonly List<Dictionary<string,int>> test8;
        public readonly List<object> test9;
        public readonly Dictionary<int,string> test10;
        public readonly Dictionary<string,List<int>> test11;
        public readonly Dictionary<int,Dictionary<string,int>> test12;
        public readonly Dictionary<string,object> test13;
        public readonly object test14;
        public readonly int test15;
        public readonly int test17;

        public test2(JSONNode buf)
        {
            test1 = (int)buf["test1"];
            test2 = (float)buf["test2"];
            test3 = (string)buf["test3"];
            test4 = (bool)buf["test4"];
            test6 = new List<int>();
            foreach (var v1 in buf["test6"])
            {
                var val1 = (int)v1.Value;
                test6.Add(val1);
            }
            test7 = new List<List<int>>();
            foreach (var v1 in buf["test7"])
            {
                var val1 = new List<int>();
                foreach (var v2 in v1.Value)
                {
                    var val2 = (int)v2.Value;
                    val1.Add(val2);
                }
                test7.Add(val1);
            }
            test8 = new List<Dictionary<string,int>>();
            foreach (var v1 in buf["test8"])
            {
                var val1 = new Dictionary<string,int>();
                foreach (var v2 in v1.Value)
                {
                    string key2 = v2.Key;
                    int val2 = (int)v2.Value;
                    val1.Add(key2,val2);
                }
                test8.Add(val1);
            }
            test9 = new List<object>();
            foreach (var v1 in buf["test9"])
            {
                var val1 = ParseValue(v1.Value);
                test9.Add(val1);
            }
            test10 = new Dictionary<int,string>();
            foreach (var v1 in buf["test10"])
            {
                int key1 = v1.Key;
                string val1 = (string)v1.Value;
                test10.Add(key1,val1);
            }
            test11 = new Dictionary<string,List<int>>();
            foreach (var v1 in buf["test11"])
            {
                string key1 = v1.Key;
                List<int> val1 = new List<int>();
                foreach (var v2 in v1.Value)
                {
                    var val2 = (int)v2.Value;
                    val1.Add(val2);
                }
                test11.Add(key1,val1);
            }
            test12 = new Dictionary<int,Dictionary<string,int>>();
            foreach (var v1 in buf["test12"])
            {
                int key1 = v1.Key;
                Dictionary<string,int> val1 = new Dictionary<string,int>();
                foreach (var v2 in v1.Value)
                {
                    string key2 = v2.Key;
                    int val2 = (int)v2.Value;
                    val1.Add(key2,val2);
                }
                test12.Add(key1,val1);
            }
            test13 = new Dictionary<string,object>();
            foreach (var v1 in buf["test13"])
            {
                string key1 = v1.Key;
                object val1 = ParseValue(v1.Value);
                test13.Add(key1,val1);
            }
            test14 = ParseValue(buf["test14"]);
            test15 = (int)buf["test15"];
            test17 = (int)buf["test17"];
        }
    }

    Dictionary<string, CfgDetail[]>  datas = new Dictionary<string, CfgDetail[]>();
    Dictionary<string, Dictionary<string, Dictionary<object, CfgDetail[]>>> dataIndex = new Dictionary<string, Dictionary<string, Dictionary<object, CfgDetail[]>>>();
    public override void Load(JSONNode buf)
    {
        datas.Add("test", new CfgDetail[buf["test"]["data"].Count]);
        dataIndex.Add("test", new Dictionary<string, Dictionary<object, CfgDetail[]>>());

        dataIndex["test"].Add("index",new Dictionary<object, CfgDetail[]>());

        for (int i = 0; i < buf["test"]["data"].Count; i++)
        {
            JSONNode item = buf["test"]["data"][i];
            test cfg = new test(item);
            datas["test"][i] = cfg;
            CfgDetail[] cfgDetails = new CfgDetail[] { cfg };
            dataIndex["test"]["index"].Add(i,cfgDetails);
        }

        dataIndex["test"].Add("test1_test3",new Dictionary<object, CfgDetail[]>());
        foreach(var v in buf["test"]["index"]["test1_test3"])
        {
            CfgDetail[] cfgDetails;
            if(v.Value.IsArray)
            {
                cfgDetails = new CfgDetail[v.Value.Count];
                for (int i = 0; i < v.Value.Count; i++)
                {
                    cfgDetails[i] = datas["test"][v.Value[i]];
                }
            }
            else
            {
                cfgDetails = new CfgDetail[]{datas["test"][v.Value]};
            }
            dataIndex["test"]["test1_test3"].Add((string)v.Key, cfgDetails);
        }
        dataIndex["test"].Add("test1",new Dictionary<object, CfgDetail[]>());
        foreach(var v in buf["test"]["index"]["test1"])
        {
            CfgDetail[] cfgDetails;
            if(v.Value.IsArray)
            {
                cfgDetails = new CfgDetail[v.Value.Count];
                for (int i = 0; i < v.Value.Count; i++)
                {
                    cfgDetails[i] = datas["test"][v.Value[i]];
                }
            }
            else
            {
                cfgDetails = new CfgDetail[]{datas["test"][v.Value]};
            }
            dataIndex["test"]["test1"].Add(int.Parse(v.Key), cfgDetails);
        }

        datas.Add("test2", new CfgDetail[buf["test2"]["data"].Count]);
        dataIndex.Add("test2", new Dictionary<string, Dictionary<object, CfgDetail[]>>());

        dataIndex["test2"].Add("index",new Dictionary<object, CfgDetail[]>());

        for (int i = 0; i < buf["test2"]["data"].Count; i++)
        {
            JSONNode item = buf["test2"]["data"][i];
            test2 cfg = new test2(item);
            datas["test2"][i] = cfg;
            CfgDetail[] cfgDetails = new CfgDetail[] { cfg };
            dataIndex["test2"]["index"].Add(i,cfgDetails);
        }

        dataIndex["test2"].Add("test1_test3",new Dictionary<object, CfgDetail[]>());
        foreach(var v in buf["test2"]["index"]["test1_test3"])
        {
            CfgDetail[] cfgDetails;
            if(v.Value.IsArray)
            {
                cfgDetails = new CfgDetail[v.Value.Count];
                for (int i = 0; i < v.Value.Count; i++)
                {
                    cfgDetails[i] = datas["test2"][v.Value[i]];
                }
            }
            else
            {
                cfgDetails = new CfgDetail[]{datas["test2"][v.Value]};
            }
            dataIndex["test2"]["test1_test3"].Add((string)v.Key, cfgDetails);
        }
        dataIndex["test2"].Add("test1",new Dictionary<object, CfgDetail[]>());
        foreach(var v in buf["test2"]["index"]["test1"])
        {
            CfgDetail[] cfgDetails;
            if(v.Value.IsArray)
            {
                cfgDetails = new CfgDetail[v.Value.Count];
                for (int i = 0; i < v.Value.Count; i++)
                {
                    cfgDetails[i] = datas["test2"][v.Value[i]];
                }
            }
            else
            {
                cfgDetails = new CfgDetail[]{datas["test2"][v.Value]};
            }
            dataIndex["test2"]["test1"].Add(int.Parse(v.Key), cfgDetails);
        }
    }

    public override int Get(string sheetName, string keyIndex, object key,out CfgDetail[] cfgDetails)
    {
        cfgDetails = null;
        if (!dataIndex.ContainsKey(sheetName))
        {
            return 1;
        }

        if (!dataIndex[sheetName].ContainsKey(keyIndex))
        {
            return 2;
        }

        if (!dataIndex[sheetName][keyIndex].TryGetValue(key, out cfgDetails))
        {
            return 3;
        }
        else
        {
            return 0;
        }
    }

    public override int GetNum(string sheetName)
    {
        if(datas.ContainsKey(sheetName))
        {
            return datas[sheetName].Length;
        }
        return 0;
    }
}