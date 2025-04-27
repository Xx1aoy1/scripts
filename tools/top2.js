
window.localStorage = window.sessionStorage = {
    removeItem: function () {
    },
    getItem: function () {
        return null
    },
    setItem: function () {
    }
};

window.open = function open() {
};
window.fetch = function fetch() {
};
window.prompt = function prompt() {
};
window.Event = function Event() {
};
window.performance = {}

window.setInterval = null_function
window.setTimeout = null_function
window.addEventListener = null_function
window.DOMParser = null_function
window.XMLHttpRequest = null_function
// window.XMLHttpRequest.prototype.open = null_function
// window.XMLHttpRequest.prototype.send = null_function
window.Request = null_function
window.clearTimeout = null_function
window.MutationObserver = function () {
    return {
        observe: function () {
            console.log(arguments)
        }
    }

}

function div() {
    return {
        getElementsByTagName(val) {
            //debugger;
            if (val === 'i') {
                return []
            }
        },
        style: {}
    }
}

HTMLFormElement = function HTMLFormElement() {
    throw  TypeError('Illegal constructor')

};
_form = {}
_form.__proto__ = HTMLFormElement.prototype

Object.defineProperty(_form, 'tagName', {
    get: function () {
        return 'FORM'
    },
    configurable: true,
    enumerable: true,
    set: undefined
})


HTMLInputElement = function HTMLInputElement() {
    throw  TypeError('Illegal constructor')
};


document.createElement = function (val) {
    //debugger;
    if (val === 'div') {
        //debugger;
        return div()
    }
    if (val === 'form') {

        return _form
    }
    if (val === 'a') {
        return {}
    }
    if (val === 'input') {
        debugger;
        input_obj = {}
        input_obj.__proto__ = HTMLInputElement.prototype
        return input_obj
    }
};
// Object.defineProperty(document.createElement,'name',{
//     value : 'createElement'
// })
document.getElementsByTagName = function (val) {
    //debugger;
    if (val === 'script' || val === 'meta') {
        return [
            {
                content: content,
                parentNode: {
                    removeChild: function () {
                    }
                },
                parentElement: {
                    removeChild: function () {
                    }
                },
                innerText : ''
            },
            {
                content: content,
                parentNode: {
                    removeChild: function () {
                    }
                },
                parentElement: {
                    removeChild: function () {
                    }
                },
                innerText : ''
            }
        ]
    }
    if (val === 'base') {
        return []
    }
}
document.getElementById = function (val) {
    if (val === 'ykBL9Y2EzdpX') {
        return {
            content: content,
            parentNode: {
                removeChild: function () {
                }
            },
            parentElement: {
                removeChild: function () {
                }
            }
        }
    }
    return null
}
document.visibilityState = 'visible';
document.cookie = "";
document.addEventListener = null_function;
document.body = {}
document.documentElement = {
    style: {}
};
document.createExpression = function () {
    return {}
}
Object.prototype.getAttribute = function (val) {
    //debugger;
    if (val === 'r') {
        return 'm'
    }
    return null
}

location = {
    "ancestorOrigins": {},
    "href": 'https://wapact.189.cn:9001/unified/user/login',
    "origin": 'https://wapact.189.cn:9001',
    "protocol": 'https:',
    "host": 'wapact.189.cn:9001',
    "hostname": 'wapact.189.cn',
    "port": '9001',
    "pathname": '/unified/user/login',
    "search": "",
    "hash": ""
}
// location.__proto__ = new Location()
Navigator = function () {
    throw TypeError('Illegal constructor')
}
navigator = {
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    languages: ["zh-CN", "zh"],
    appVersion: "5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    appName: "Netscape",
    vendor: "Google Inc.",
    connection: {
        downlink: 10,
        effectiveType: "4g",
        rtt: 200,
        saveData: false,
    },
    mimeTypes: {},
    platform: 'Win32',
    webkitPersistentStorage: {}

}
window.clientInformation = navigator;
navigator.__proto__ = Navigator.prototype
Object.defineProperty(Navigator.prototype, 'webdriver', {
    get: function webdriver() {
    },
    configurable: true,
    enumerable: true,
    set: undefined

})
Object.defineProperty(Navigator.prototype, 'languages', {
    get: function languages() {
    },
    configurable: true,
    enumerable: true,
    set: undefined

})
Object.defineProperty(Navigator.prototype, 'vendor', {
    get: function vendor() {
    },
    configurable: true,
    enumerable: true,
    set: undefined

})
Object.defineProperty(navigator.__proto__, 'webdriver', {
    get: function webdriver() {
        return false;
    },
    configurable: true,
    enumerable: true,
    set: undefined

})

// History = function () {
// };
history = {
    replaceState: function () {
    }
};
// history.__proto__ = new History()

Error.prepareStackTrace = function (error, structuredStackTrace) {
    console.log("有报错, 错误已打印，可以考虑在此处拦截\n", error.stack)
    //error.stack = error.stack.replace(/vm.js/g, "<anonymous>")
    error.stack = error.stack.split('\n')[0] + '\n    at <anonymous>:1:1';
    console.log("有报错,已拦截，替换为\n", error.stack)
    return error.stack
};

let _lp_func_toString = Object.assign(Function.prototype.toString);
Function.prototype.toString = function Function() {
    let func_name = this.name
    if (func_name === 'languages' || func_name === 'vendor' || func_name === 'webdriver') {
        console.log(`Function toString ${func_name} 被调用`)
        console.log(`返回：` + `function get ${func_name}() { [native code] }`)
        return `function get ${func_name}() { [native code] }`
    }
    if (func_name === 'open' || func_name === 'prompt' || func_name === 'Event' || func_name === "clearInterval" || func_name === "Request" || func_name === 'fetch' || func_name === 'eval' || func_name === 'getImageData' || func_name === 'toBlob' || func_name === 'toDataURL') {
        console.log(`Function toString ${func_name} 被调用`)
        console.log(`返回：` + `function ${func_name}() { [native code] }`)
        return `function ${func_name}() { [native code] }`
    }
    if (func_name === 'Function') {

        //debugger;
        return `function ${func_name}() { [native code] }`

    }
    // debugger;
    //         console.log("函数体为（只展示50字符）：" + _lp_func_toString.call(this).slice(0, 100))
    //
    // console.log("原路返回")
    return _lp_func_toString.call(this)

}


my_Proxy(['window', 'navigator', 'location', 'document', 'history', '_form'])

