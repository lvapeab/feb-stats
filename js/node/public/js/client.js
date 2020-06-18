Dropzone.options.uploadWidget = {
    paramName: 'file',
    maxFilesize: 10, // MB
    maxFiles: 500,
    dictDefaultMessage: 'Arrastra aquí los archivos a subir o haz click para seleccionarlos.',
    headers: {
        'x-csrf-token': document.querySelector('meta[name=csrf-token]').getAttributeNode('content').value,
    },
    acceptedFiles: 'image/*, text/html',
    init: function () {
        this.on('success', function (file) {
                console.log(file);
            }
        )
    }
};
//
    //
// var BoxscoresInput = document.getElementById('boxscores-input');
// BoxscoresInput.addEventListener('change', function (e) {
//     var uploaded_files = [];
//     const files = e.currentTarget.files;
//     Object.keys(files).forEach(i => {
//         const file = files[i];
//         const reader = new FileReader();
//         reader.onload = (e) => {
//             uploaded_files.push(reader.result);
//         };
//         reader.readAsBinaryString(file);
//     });
//     const url = "/analyze_stats";
//     // post form data
//     const xhr = new XMLHttpRequest();
//     xhr.responseType = 'blob';
//     // log response
//     xhr.onload = () => {
//         console.log(xhr.responseText);
//     };
//
//     // create and send the reqeust
//     xhr.open('POST', url);
//     xhr.send(uploaded_files);
//
// });
