<!doctype html>
<html lang="pt-br">

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>UX-Tracking: Web and Multimodal Tool for User Experience Evaluation</title>
    <link rel="stylesheet" href="css/index.css" />
</head>

<body>
    <div id="particles-js"></div>
    <div id="logo">
        <img src="logo.png">
    </div>
    <div id="div-botoes">
        <ul class="menu">
            <form method='post' action=''>
                <input class="botoes-menu" type='submit' name='downloadResearch' value='Download Research' />&nbsp;
                <input class="botoes-menu" type='submit' name='downloadExtension' value='Extensão' />&nbsp;
                <input class="botoes-menu" type='submit' name='downloadTools' value='Ferramentas de Pós-processamento' />&nbsp;
                <a href="https://github.com/Colab-UNIRIO-UFPA/UX-Tracking#readme" onclick="link(this)">
                    <button class="botoes-menu">Manual de Uso</button>
                </a>
                <a href="https://github.com/Colab-UNIRIO-UFPA/UX-Tracking" onclick="link(this)">
                    <button class="botoes-menu">Repositório</button>
                </a>
            </form>
        </ul>
    </div>
    &nbsp;
    <div class="texto">
        <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            A UX-Tracking é uma ferramenta que monitora, de forma automatizada, a
            experiência do usuário (neste caso, desenvolvedor) no ambiente Web e
            gera artefatos visuais e indicadores para documentá-la, permitindo a
            realização de análises e diagnósticos sobre a percepção do desenvolvedor
            de quão fácil é navegar em um portal e se há algum problema que gere uma
            experiência ruim. A ferramenta é composta por três módulos principais: o
            módulo cliente, o módulo de armazenamento e o módulo de visualizacão de
            dados, que são os responsÃ¡veis por capturar as interações dos desenvolvedores,
            armazenar e disponibilizar os resultados da interação, respectivamente (SOUZA et al, 2020).</p>
        <p>Possíveis variáveis que a ferramenta pode coletar:</p>
        <ul>
            <li>Distância total do mouse</li>
            <li>Atraso na decisão de clicar</li>
            <li>Número total de cliques</li>
            <li>Tempo de fixação do olhar</li>
        </ul>
    </div>
    <div class='container'>
    </div>
</body>
    <script type="text/javascript" src="js/particles.js"></script>
	<script type="text/javascript" src="js/app.js"></script>
	<script type="text/javascript" src="js/opener.js"></script>
    
</html>

<?php
// Create ZIP file
if (isset($_POST['downloadResearch'])) {
    $zip = new ZipArchive();
    $filename = "./research.zip";

    if ($zip->open($filename, ZipArchive::CREATE) !== TRUE) {
        exit("cannot open <$filename>\n");
    }

    $dir = 'Samples/';

    // Create zip
    createZip($zip, $dir);

    $zip->close();

    $filename = "research.zip";

    if (file_exists($filename)) {
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
        header('Content-Length: ' . filesize($filename));

        flush();
        readfile($filename);
        // delete file
        unlink($filename);
    }

    $dir = "./Samples";

    $structure = glob(rtrim($dir, "/") . '/*');
    if (is_array($structure)) {
        foreach ($structure as $file) {
            if (is_dir($file)) recursiveRemove($file);
            elseif (is_file($file)) unlink($file);
        }
    }
    rmdir($dir);
}

if (isset($_POST['downloadExtension'])) {
    $filename = "UX-Tracking Extension.zip";
    if (file_exists($filename)) {
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
        header('Content-Length: ' . filesize($filename));

        flush();
        readfile($filename);
    }
}

if (isset($_POST['downloadTools'])) {
    $filename = "UX-Tracking Tools.zip";
    if (file_exists($filename)) {
        header('Content-Type: application/zip');
        header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
        header('Content-Length: ' . filesize($filename));

        flush();
        readfile($filename);
    }
}

// Create zip
function createZip($zip, $dir)
{
    if (is_dir($dir)) {

        if ($dh = opendir($dir)) {
            while (($file = readdir($dh)) !== false) {

                // If file
                if (is_file($dir . $file)) {
                    if ($file != '' && $file != '.' && $file != '..') {

                        $zip->addFile($dir . $file);
                    }
                } else {
                    // If directory
                    if (is_dir($dir . $file)) {

                        if ($file != '' && $file != '.' && $file != '..') {

                            // Add empty directory
                            $zip->addEmptyDir($dir . $file);

                            $folder = $dir . $file . '/';

                            // Read data of the folder
                            createZip($zip, $folder);
                        }
                    }
                }
            }
            closedir($dh);
        }
    }
}


function recursiveRemove($dir)
{
    $structure = glob(rtrim($dir, "/") . '/*');
    if (is_array($structure)) {
        foreach ($structure as $file) {
            if (is_dir($file)) recursiveRemove($file);
            elseif (is_file($file)) unlink($file);
        }
    }
    rmdir($dir);
}

?>
