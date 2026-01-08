<?php
$data = json_decode(file_get_contents("php://input"), true);

if (!$data) {
    http_response_code(400);
    exit;
}

$entry = [
    "received_at" => gmdate("c"),
    "data" => $data
];

// Guardado plano (válido para hosting gratuito)
file_put_contents(
    "fingerprints.log",
    json_encode($entry, JSON_UNESCAPED_SLASHES) . PHP_EOL,
    FILE_APPEND | LOCK_EX
);

header("Content-Type: application/json");
echo json_encode(["status" => "ok"]);
