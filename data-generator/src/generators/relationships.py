from typing import Dict, List, Any


class DataState:
    """Maintains state across data generation to ensure referential integrity"""
    
    def __init__(self):
        self.generated_orders: List[Dict[str, Any]] = []
        self.generated_payments: List[Dict[str, Any]] = []
        self.user_ids = list(range(1, 1001))  # Pool of user IDs
        self.product_ids = list(range(1, 501))  # Pool of product IDs
    
    def store_generated_data(self, model_name: str, instance_dict: Dict[str, Any]):
        """Store generated instances for relationship building"""
        if model_name.lower() == "order":
            self.generated_orders.append(instance_dict)
        elif model_name.lower() == "payment":
            self.generated_payments.append(instance_dict)
    
    def get_completed_orders(self) -> List[Dict[str, Any]]:
        """Get orders with completed status for return generation"""
        return [o for o in self.generated_orders if o.get('status') == 'completed']
    
    def reset(self):
        """Reset all generated data - useful for new scenarios"""
        self.generated_orders.clear()
        self.generated_payments.clear()


# Global data state instance
data_state = DataState()