# Complete Command Reference

## Quick Reference Summary

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `list-models` | Show available models | None |
| `register` | Register Avro schemas | None (Avro only) |
| `generate` | Generate data for one model | `--model`, `--count` |
| `scenario` | Generate realistic e-commerce data | `--orders`, `--payments`, `--returns` |

## Environment Variables

| Variable | Values | Purpose |
|----------|---------|---------|
| `SERIALIZATION_FORMAT` | `avro`, `json` | Output format |
| `DATA_GEN_DELAY_MS` | Number (default: 100) | Delay between records |
| `DATA_GEN_BATCH_SIZE` | Number (default: 100) | Batch size |


### **1. List Available Models**
```bash
docker exec -it data-generator python src/main.py list-models
```

### **2. Register Schemas (Avro only)**
```bash
docker exec -it data-generator python src/main.py register
```

### **3. Generate Individual Model Data**

**Basic generation (5 records default):**
```bash
docker exec -it data-generator python src/main.py generate --model user
docker exec -it data-generator python src/main.py generate --model product
docker exec -it data-generator python src/main.py generate --model order
docker exec -it data-generator python src/main.py generate --model payment
docker exec -it data-generator python src/main.py generate --model return
```

**Custom count:**
```bash
docker exec -it data-generator python src/main.py generate --model user --count 50
docker exec -it data-generator python src/main.py generate --model product --count 100
docker exec -it data-generator python src/main.py generate --model order --count 25
docker exec -it data-generator python src/main.py generate --model payment --count 30
docker exec -it data-generator python src/main.py generate --model return --count 10
```

### **4. Generate Realistic Scenarios**

**Default scenario (100 orders, 120 payments, 15 returns):**
```bash
docker exec -it data-generator python src/main.py scenario
```

**Custom scenario:**
```bash
docker exec -it data-generator python src/main.py scenario --orders 200 --payments 250 --returns 30
docker exec -it data-generator python src/main.py scenario --orders 50 --payments 60 --returns 5
docker exec -it data-generator python src/main.py scenario --orders 500 --payments 600 --returns 75
```

### **5. Environment Variable Overrides**

**Switch serialization format temporarily:**
```bash
# JSON serialization (one-time)
docker exec -it -e SERIALIZATION_FORMAT=json data-generator python src/main.py generate --model user --count 10

# Avro serialization (one-time)
docker exec -it -e SERIALIZATION_FORMAT=avro data-generator python src/main.py generate --model user --count 10
```

**Multiple environment overrides:**
```bash
docker exec -it -e SERIALIZATION_FORMAT=json -e DATA_GEN_DELAY_MS=50 data-generator python src/main.py generate --model order --count 100
```

### **6. Batch Command Examples**

**Complete setup workflow:**
```bash
# 1. Register schemas (if using Avro)
docker exec -it data-generator python src/main.py register

# 2. Generate base data
docker exec -it data-generator python src/main.py generate --model user --count 100
docker exec -it data-generator python src/main.py generate --model product --count 50

# 3. Generate realistic scenario
docker exec -it data-generator python src/main.py scenario --orders 150 --payments 180 --returns 20
```

**Switch between formats and generate:**
```bash
# Generate Avro data
docker exec -it data-generator python src/main.py register
docker exec -it data-generator python src/main.py generate --model user --count 25

# Generate JSON data  
docker exec -it -e SERIALIZATION_FORMAT=json data-generator python src/main.py generate --model user --count 25
```

### **7. Help Commands**
```bash
# Main help
docker exec -it data-generator python src/main.py --help

# Command-specific help
docker exec -it data-generator python src/main.py generate --help
docker exec -it data-generator python src/main.py scenario --help
```


## Output Topics

**Avro format:** `{model}_avro_topic` (e.g., `user_avro_topic`)  
**JSON format:** `{model}_json_topic` (e.g., `user_json_topic`)