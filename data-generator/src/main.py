import argparse
import sys

from config.settings import settings
from commands import register_schemas, generate_data, generate_realistic_scenario
from models import ALL_MODELS


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🏭 DATA GENERATOR")
    print("=" * 60)
    print(f"Environment: {settings.environment}")
    print(f"Serialization: {settings.serialization_format}")
    print(f"Kafka Broker: {settings.kafka_broker}")
    if settings.serialization_format == "avro":
        print(f"Schema Registry: {settings.schema_registry_url}")
    print("=" * 60)
    print()


def cmd_register(args):
    """Handle schema registration command"""
    print("📋 Registering schemas...")
    register_schemas()


def cmd_generate(args):
    """Handle data generation command"""
    if not args.model:
        print("❌ Model name is required for generate command")
        sys.exit(1)
    
    generate_data(args.model, args.count)


def cmd_scenario(args):
    """Handle scenario generation command"""
    generate_realistic_scenario(args.orders, args.payments, args.returns)


def cmd_list_models(args):
    """List available models"""
    print("📋 Available models:")
    for model in ALL_MODELS:
        print(f"   • {model.__name__}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced data generator for Kafka",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py register                           # Register schemas
  python main.py generate --model user --count 50   # Generate 50 users
  python main.py scenario --orders 100              # Generate scenario
  python main.py list-models                        # Show available models
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Register schemas command
    register_parser = subparsers.add_parser("register", help="Register Avro schemas")
    register_parser.set_defaults(func=cmd_register)
    
    # Generate data command
    generate_parser = subparsers.add_parser("generate", help="Generate data for a model")
    generate_parser.add_argument("--model", type=str, required=True, 
                               help="Model name (e.g., User, Order, Payment)")
    generate_parser.add_argument("--count", type=int, default=5, 
                               help="Number of records to generate")
    generate_parser.set_defaults(func=cmd_generate)
    
    # Scenario generation command
    scenario_parser = subparsers.add_parser("scenario", help="Generate realistic e-commerce scenario")
    scenario_parser.add_argument("--orders", type=int, default=100, 
                               help="Number of orders to generate")
    scenario_parser.add_argument("--payments", type=int, default=120, 
                               help="Number of payments to generate")
    scenario_parser.add_argument("--returns", type=int, default=15, 
                               help="Number of returns to generate")
    scenario_parser.set_defaults(func=cmd_scenario)
    
    # List models command
    list_parser = subparsers.add_parser("list-models", help="List available models")
    list_parser.set_defaults(func=cmd_list_models)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show banner
    print_banner()
    
    # Execute command
    if hasattr(args, 'func'):
        try:
            args.func(args)
        except KeyboardInterrupt:
            print("\n⏹️  Operation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()