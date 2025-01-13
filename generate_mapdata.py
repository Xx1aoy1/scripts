import random
addresses =[
    {
        "provice_name": "北京市",
        "city_name": "北京市",
        "area_name": "朝阳区",
        "address": "北京市朝阳区建国路88号",
        "longitude": "116.4551",
        "dimension": "39.9185"
    },
    {
        "provice_name": "天津市",
        "city_name": "天津市",
        "area_name": "和平区",
        "address": "天津市和平区南京路66号",
        "longitude": "117.2025",
        "dimension": "39.1248"
    },
    {
        "provice_name": "河北省",
        "city_name": "石家庄市",
        "area_name": "长安区",
        "address": "河北省石家庄市长安区中山东路200号",
        "longitude": "114.5149",
        "dimension": "38.0428"
    },
    {
        "provice_name": "山西省",
        "city_name": "太原市",
        "area_name": "迎泽区",
        "address": "山西省太原市迎泽区迎泽大街50号",
        "longitude": "112.5489",
        "dimension": "37.8706"
    },
    {
        "provice_name": "内蒙古自治区",
        "city_name": "呼和浩特市",
        "area_name": "赛罕区",
        "address": "内蒙古自治区呼和浩特市赛罕区大学东街100号",
        "longitude": "111.7519",
        "dimension": "40.8415"
    },
    {
        "provice_name": "辽宁省",
        "city_name": "沈阳市",
        "area_name": "和平区",
        "address": "辽宁省沈阳市和平区太原南街200号",
        "longitude": "123.4328",
        "dimension": "41.8086"
    },
    {
        "provice_name": "吉林省",
        "city_name": "长春市",
        "area_name": "朝阳区",
        "address": "吉林省长春市朝阳区西安大路88号",
        "longitude": "125.3245",
        "dimension": "43.8868"
    },
    {
        "provice_name": "黑龙江省",
        "city_name": "哈尔滨市",
        "area_name": "南岗区",
        "address": "黑龙江省哈尔滨市南岗区中山路58号",
        "longitude": "126.6424",
        "dimension": "45.7564"
    },
    {
        "provice_name": "上海市",
        "city_name": "上海市",
        "area_name": "浦东新区",
        "address": "上海市浦东新区世纪大道100号",
        "longitude": "121.4737",
        "dimension": "31.2304"
    },
    {
        "provice_name": "江苏省",
        "city_name": "南京市",
        "area_name": "玄武区",
        "address": "江苏省南京市玄武区中山路101号",
        "longitude": "118.7969",
        "dimension": "32.0603"
    },
    {
        "provice_name": "浙江省",
        "city_name": "杭州市",
        "area_name": "西湖区",
        "address": "浙江省杭州市西湖区龙井路1号",
        "longitude": "120.1551",
        "dimension": "30.2741"
    },
    {
        "provice_name": "安徽省",
        "city_name": "合肥市",
        "area_name": "蜀山区",
        "address": "安徽省合肥市蜀山区黄山路118号",
        "longitude": "117.2830",
        "dimension": "31.8612"
    },
    {
        "provice_name": "福建省",
        "city_name": "福州市",
        "area_name": "鼓楼区",
        "address": "福建省福州市鼓楼区五一北路88号",
        "longitude": "119.2965",
        "dimension": "26.0745"
    },
    {
        "provice_name": "江西省",
        "city_name": "南昌市",
        "area_name": "青山湖区",
        "address": "江西省南昌市青山湖区南京东路188号",
        "longitude": "115.8582",
        "dimension": "28.6829"
    },
    {
        "provice_name": "山东省",
        "city_name": "济南市",
        "area_name": "历下区",
        "address": "山东省济南市历下区泉城路200号",
        "longitude": "117.0009",
        "dimension": "36.6758"
    },
    {
        "provice_name": "河南省",
        "city_name": "郑州市",
        "area_name": "金水区",
        "address": "河南省郑州市金水区东风路88号",
        "longitude": "113.6254",
        "dimension": "34.7466"
    },
    {
        "provice_name": "湖北省",
        "city_name": "武汉市",
        "area_name": "江汉区",
        "address": "湖北省武汉市江汉区新华路100号",
        "longitude": "114.3054",
        "dimension": "30.5931"
    },
    {
        "provice_name": "湖南省",
        "city_name": "长沙市",
        "area_name": "天心区",
        "address": "湖南省长沙市天心区五一路300号",
        "longitude": "112.9823",
        "dimension": "28.1941"
    },
    {
        "provice_name": "广东省",
        "city_name": "广州市",
        "area_name": "天河区",
        "address": "广东省广州市天河区体育东路200号",
        "longitude": "113.2644",
        "dimension": "23.1292"
    },
    {
        "provice_name": "广西壮族自治区",
        "city_name": "南宁市",
        "area_name": "青秀区",
        "address": "广西壮族自治区南宁市青秀区民族大道100号",
        "longitude": "108.3669",
        "dimension": "22.8167"
    },
    {
        "provice_name": "海南省",
        "city_name": "海口市",
        "area_name": "美兰区",
        "address": "海南省海口市美兰区国兴大道50号",
        "longitude": "110.3312",
        "dimension": "20.0313"
    },
    {
        "provice_name": "重庆市",
        "city_name": "重庆市",
        "area_name": "渝中区",
        "address": "重庆市渝中区解放碑步行街200号",
        "longitude": "106.5516",
        "dimension": "29.5630"
    },
    {
        "provice_name": "四川省",
        "city_name": "成都市",
        "area_name": "锦江区",
        "address": "四川省成都市锦江区天府大道1000号",
        "longitude": "104.0665",
        "dimension": "30.5728"
    },
    {
        "provice_name": "贵州省",
        "city_name": "贵阳市",
        "area_name": "南明区",
        "address": "贵州省贵阳市南明区中山路88号",
        "longitude": "106.7135",
        "dimension": "26.5783"
    },
    {
        "provice_name": "云南省",
        "city_name": "昆明市",
        "area_name": "五华区",
        "address": "云南省昆明市五华区青年路200号",
        "longitude": "102.8329",
        "dimension": "24.8801"
    },
    {
        "provice_name": "西藏自治区",
        "city_name": "拉萨市",
        "area_name": "城关区",
        "address": "西藏自治区拉萨市城关区北京中路100号",
        "longitude": "91.1322",
        "dimension": "29.6604"
    },
    {
        "provice_name": "陕西省",
        "city_name": "西安市",
        "area_name": "雁塔区",
        "address": "陕西省西安市雁塔区长安南路88号",
        "longitude": "108.9402",
        "dimension": "34.3416"
    },
    {
        "provice_name": "甘肃省",
        "city_name": "兰州市",
        "area_name": "城关区",
        "address": "甘肃省兰州市城关区东岗西路58号",
        "longitude": "103.8343",
        "dimension": "36.0611"
    },
    {
        "provice_name": "青海省",
        "city_name": "西宁市",
        "area_name": "城东区",
        "address": "青海省西宁市城东区八一路50号",
        "longitude": "101.7782",
        "dimension": "36.6173"
    },
    {
        "provice_name": "宁夏回族自治区",
        "city_name": "银川市",
        "area_name": "兴庆区",
        "address": "宁夏回族自治区银川市兴庆区解放路88号",
        "longitude": "106.2309",
        "dimension": "38.4872"
    },
    {
        "provice_name": "新疆维吾尔自治区",
        "city_name": "乌鲁木齐市",
        "area_name": "天山区",
        "address": "新疆维吾尔自治区乌鲁木齐市天山区解放北路200号",
        "longitude": "87.6168",
        "dimension": "43.8256"
    },
    {
        "provice_name": "香港特别行政区",
        "city_name": "香港",
        "area_name": "中西区",
        "address": "香港特别行政区中西区皇后大道中100号",
        "longitude": "114.1694",
        "dimension": "22.3193"
    },
    {
        "provice_name": "澳门特别行政区",
        "city_name": "澳门",
        "area_name": "花地玛堂区",
        "address": "澳门特别行政区花地玛堂区新马路300号",
        "longitude": "113.5491",
        "dimension": "22.1987"
    },
    {
        "provice_name": "台湾省",
        "city_name": "台北市",
        "area_name": "中正区",
        "address": "台湾省台北市中正区忠孝东路100号",
        "longitude": "121.5654",
        "dimension": "25.0329"
    }
]

def get_random_address():
    return random.choice(addresses)
def generate_code():
    fixed_part = "241210183"
    random_part = str(random.randint(10000, 99999))
    return f"SCENE-{fixed_part}{random_part}"

def generate_mapdata(province=None):


    if province is None:
        selected_address = get_random_address()
    else:
        
        filtered_addresses = [addr for addr in addresses if addr["provice_name"] == province]
        if filtered_addresses:
            selected_address = random.choice(filtered_addresses)
        else:
            
            selected_address = get_random_address()


    mapdata = {
        "code": 'SCENE-24121018345681',
        "provice_name": selected_address["provice_name"],
        "city_name": selected_address["city_name"],
        "area_name": selected_address["area_name"],
        "address": selected_address["address"],
        "longitude": selected_address["longitude"],
        "dimension": selected_address["dimension"]
    }
    return mapdata