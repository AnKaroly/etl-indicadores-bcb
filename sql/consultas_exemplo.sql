-- Consultas para praticar SQL em cima do banco gerado (sqlite3 data/indicadores.db)

-- 1. Quantidade de registros e período coberto por série
SELECT serie, COUNT(*) AS registros, MIN(data) AS inicio, MAX(data) AS fim
FROM indicadores
GROUP BY serie;

-- 2. Média anual do dólar
SELECT substr(data, 1, 4) AS ano, ROUND(AVG(valor), 4) AS dolar_medio
FROM indicadores
WHERE serie = 'dolar'
GROUP BY ano
ORDER BY ano;

-- 3. Mudanças na meta Selic (usa função de janela LAG)
SELECT data, valor AS selic, anterior
FROM (
    SELECT data, valor, LAG(valor) OVER (ORDER BY data) AS anterior
    FROM indicadores
    WHERE serie = 'selic'
)
WHERE anterior IS NULL OR valor <> anterior;
