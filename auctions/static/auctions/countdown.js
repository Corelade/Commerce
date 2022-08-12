
document.querySelector('#bid_button').onclick = ()=> setInterval(timer, 1000);
function SecondsConverter(secs){
    if (`${secs}` < 3600){
        let m = Math.floor(`${secs}`/60);
        let s = `${secs}` % 60;
        let answer = `${m}m:${s}s`;
        return answer
    }
    else{
        let h = Math.floor(`${secs}`/3600);
        let rem = `${secs}` % 3600;
        let min = Math.floor(rem/60);
        let sec = `${secs}`% 60;
        let answer = `${h}h:${min}m:${sec}s`;
        return answer
    }
}
var time = 30;
function timer(){
    if (time > 0){
        time = time - 1;
        document.querySelector('#countdown').innerHTML = 'Auction will close in' +' '+ SecondsConverter(time);
    }
    else{
        document.querySelector('#countdown').innerHTML = 'Auction has ended';
    }
}  