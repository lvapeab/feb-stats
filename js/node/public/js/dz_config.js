Dropzone.options.uploadWidget = {
    paramName: 'file',
    maxFilesize: 10, // MB
    parallelUploads:500,
    autoDiscover: false,
    uploadMultiple:true,
    maxFiles: 500,
    dictDefaultMessage: 'Arrastra aquí los archivos a subir o haz click para seleccionarlos.',
    headers: {
        'x-csrf-token': document.querySelector('meta[name=csrf-token]').getAttributeNode('content').value,
    },
    acceptedFiles: 'image/*,text/html',
    init: function () {
        this.on('success', function (file) {
                console.log(file);
            }
        )
    }
};
