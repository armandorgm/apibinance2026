import os

file_path = "f:/apibinance2026/backend/app/services/pipeline_engine/actions.py"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix handle_tick
for i, line in enumerate(lines):
    if "async def handle_tick(self," in line:
        lines[i] = "    @staticmethod\n    async def handle_tick(process, current_price: float, session):\n"
    if "await self._execute_order_replacement(" in line:
        lines[i] = line.replace("await self._execute_order_replacement(", "await AdaptiveOTOScalingAction._execute_order_replacement(")
    if "async def handle_order_event(self," in line:
        lines[i] = "    @staticmethod\n    async def handle_order_event(process, order_data: Dict[str, Any], session):\n"
    if "await self.handle_fill(" in line:
        lines[i] = line.replace("await self.handle_fill(", "await AdaptiveOTOScalingAction.handle_fill(")
    if "await self.handle_abort(" in line:
        lines[i] = line.replace("await self.handle_abort(", "await AdaptiveOTOScalingAction.handle_abort(")
    if "async def _execute_order_replacement(self," in line:
        lines[i] = "    @staticmethod\n    async def _execute_order_replacement(process, target_price: float, session, reason: str = \"Chase\"):\n"
    # Convert print to logger
    if 'print(f"[CHASE] Entry FILLED' in line:
        lines[i] = line.replace('print(f"[CHASE] Entry FILLED', 'logger.info(f"[CHASE] Entry FILLED')
    if 'print(f"[CHASE] Completed OTO' in line:
        lines[i] = line.replace('print(f"[CHASE] Completed OTO', 'logger.info(f"[CHASE] Completed OTO')
    if 'print(f"[CHASE] Entry aborted' in line:
        lines[i] = line.replace('print(f"[CHASE] Entry aborted', 'logger.warning(f"[CHASE] Entry aborted')

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Replacement complete.")
