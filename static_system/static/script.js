function navigate(path) {
      window.location.href = `http://${window.location.host}/${path}`;
    }
function refresh(path){
   switch(path){
        case 0:
            window.location.href = `http://${window.location.host}/`
            break;
        case 1:
            window.location.href=`http://${window.location.host}/page/lucroPresumido`
            break;
        case 2:
            window.location.href=`http://${window.location.host}/page/simplesNacional`
            break;
    } 
}