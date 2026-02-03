#!/bin/bash

# Colores para impresionar
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "🚀 \033[1mINICIANDO PRUEBA DE SISTEMA DISTRIBUIDO\033[0m"
echo "=================================================="

# 1. Verificar que los Pods existen
echo -n "🔍 Verificando Pods..."
PODS_COUNT=$(kubectl get pods | grep Running | wc -l)
if [ "$PODS_COUNT" -ge 3 ]; then
    echo -e "${GREEN} OK ($PODS_COUNT pods activos)${NC}"
else
    echo -e "${RED} FALLO (Faltan pods, revisa 'kubectl get pods')${NC}"
    exit 1
fi

# 2. Verificar Health Checks (Si implementaste el endpoint /health)
# Nota: Esto asume que tienes el port-forward corriendo en segundo plano
echo -n "❤️  Verificando Salud del Receiver (localhost:8080)..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)

if [ "$HTTP_STATUS" == "200" ]; then
    echo -e "${GREEN} VIVO (200 OK)${NC}"
else
    echo -e "${RED} MUERTO (Status: $HTTP_STATUS) - ¿Corriste el port-forward?${NC}"
    echo "   Tip: Ejecuta 'kubectl port-forward svc/receiver-svc 8080:5000' en otra terminal."
fi

# 3. Prueba Funcional (El Ciclo Completo)
echo ""
echo "⚡ Disparando prueba de ciclo (A -> B -> C)..."
echo "   Payload: { \"id\": \"test-auto\", \"value\": 10 }"

RESPONSE=$(curl -s -X POST http://localhost:8080/start \
     -H "Content-Type: application/json" \
     -d '{
           "id": "test-auto",
           "value": 10,
           "audit": []
         }')

# Analizar respuesta
if [[ "$RESPONSE" == *"FINISHED"* ]]; then
    echo -e "${GREEN}✅ ÉXITO TOTAL: El ciclo se completó.${NC}"
    echo "📄 Respuesta del sistema:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo -e "${RED}❌ FALLO: No se recibió confirmación de finalización.${NC}"
    echo "📄 Respuesta recibida: $RESPONSE"
fi

echo ""
echo "=================================================="