<?php
$server_data = [
    "ip_remote"      => $_SERVER['REMOTE_ADDR'] ?? '',
    "x_forwarded_for"=> $_SERVER['HTTP_X_FORWARDED_FOR'] ?? '',
    "user_agent"     => $_SERVER['HTTP_USER_AGENT'] ?? '',
    "accept_lang"    => $_SERVER['HTTP_ACCEPT_LANGUAGE'] ?? '',
    "referer"        => $_SERVER['HTTP_REFERER'] ?? '',
];
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Client Fingerprint</title>
    <script>
        const SERVER_DATA = <?= json_encode($server_data, JSON_PRETTY_PRINT) ?>;
    </script>
    <script src="fingerprint.js" defer></script>
    <style>
        body { font-family: monospace; background:#0f172a; color:#e5e7eb; }
        pre { background:#020617; padding:1rem; overflow:auto; }
    </style>
</head>
<body>
<h2>Client Fingerprint</h2>
<pre id="output">Recolectando…</pre>
</body>
</html>
