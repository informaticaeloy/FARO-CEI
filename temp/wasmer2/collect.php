<?php
header("Content-Type: application/json");

$raw = file_get_contents("php://input");
$data = json_decode($raw, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(["status" => "error", "msg" => "JSON inválido"]);
    exit;
}

$evento = [
    "timestamp"   => date("c"),
    "ip"          => $_SERVER["REMOTE_ADDR"] ?? null,
    "hostname_rdns" => gethostbyaddr($_SERVER["REMOTE_ADDR"] ?? ""),
    "visitorId"   => $data["visitorId"] ?? null,
    "confidence"  => $data["confidence"] ?? null,
    "userAgent"   => $data["userAgent"] ?? null,
    "timezone"    => $data["timezone"] ?? null,
    "payload"     => $data
];

// Persistencia simple (append)
file_put_contents(
    "fingerprints.log",
    json_encode($evento, JSON_UNESCAPED_UNICODE) . PHP_EOL,
    FILE_APPEND
);

echo json_encode(["status" => "ok"]);
