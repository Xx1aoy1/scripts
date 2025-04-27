const v8 =require('v8');
const vm=require('vm');
v8.setFlagsFromString('--allow-natives-syntax');
let undetectable = vm.runInThisContext("%GetUndetectable()");
v8.setFlagsFromString('--no-allow-natives-syntax');
my_Proxy=function (){}
delete __filename;
delete __dirname;
delete process;
res_log = console.log
console.log=function (){};
// Window = function Window() {
// }
window = globalThis;
// window.__proto__ = new Window()
// global = window;
delete global


document = {
    characterSet: 'UTF-8',
    charset: 'UTF-8',
    scripts: ['script', 'script'],
    appendChild: function () {
        debugger;
        if (arguments[0].id === 'username') {
            this.action = arguments[0]
        } else if (arguments[0].id === 'password') {

            this.textContent = arguments[0]

        } else if (arguments[0].id === 'innerText') {

            this.id = arguments[0]
            this.innerText = arguments[0]

        }


    },
    removeChild: function () {
    }
};
document['all'] = undetectable
document.all[0] = 'html'
document.all[1] =  'head'
document.all[2] = 'meta'

Object.defineProperty(document.all,'length',{
    get : function (){
        return Object.keys(document.all).length
    }
})
null_function = function () {
    console.log(arguments)
}
// HTMLDocument = function () {
// }

// document.__proto__ = new HTMLDocument()

window.ActiveXObject = undefined;
// delete ActiveXObject
window.clearImmediate = undefined;
window.setImmediate = undefined;
window.top = window;
window.self = window;
window.name = "";
window.TEMPORARY = 0;
window.indexedDB = {};
window.chrome = {};
window.innerHeight = 930;
window.innerWidth = 681;
window.outerHeight = 1059;
window.outerWidth = 2208;
window.name = '';


// Object.defineProperty(window.Event, 'name', {
//     value: 'Event'
// });

window.CanvasRenderingContext2D = function () {
}
window.CanvasRenderingContext2D.prototype = {
    getImageData: function () {
    }
};
window.HTMLCanvasElement = function () {
}
window.HTMLCanvasElement.prototype = {
    toBlob: function () {
    },
    toDataURL: function () {
    }
}