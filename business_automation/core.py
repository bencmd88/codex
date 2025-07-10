service"""
Core functionality for business automation.
"""
import logging
import os
import datetime
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'automation.log'))
    ]
)
logger = logging.getLogger('business_automation')

class AutomationTask:
    """Base class for all automation tasks"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.created_at = datetime.datetime.now()
        self.last_run = None
        self.status = "initialized"
        self.results = None
        logger.info(f"Task '{name}' initialized")
    
    def run(self, *args, **kwargs) -> Any:
        """Execute the task. Should be overridden by subclasses."""
        self.last_run = datetime.datetime.now()
        self.status = "running"
        logger.info(f"Running task '{self.name}'")
        
        try:
            result = self._execute(*args, **kwargs)
            self.status = "completed"
            self.results = result
            logger.info(f"Task '{self.name}' completed successfully")
            return result
        except Exception as e:
            self.status = "failed"
            logger.error(f"Task '{self.name}' failed: {str(e)}", exc_info=True)
            raise
    
    def _execute(self, *args, **kwargs) -> Any:
        """Internal execution method. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _execute method")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "status": self.status,
            "results": self.results
        }

class AutomationWorkflow:
    """Manages a sequence of automation tasks"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tasks: List[AutomationTask] = []
        self.created_at = datetime.datetime.now()
        self.last_run = None
        logger.info(f"Workflow '{name}' initialized")
    
    def add_task(self, task: AutomationTask) -> None:
        """Add a task to the workflow"""
        self.tasks.append(task)
        logger.info(f"Added task '{task.name}' to workflow '{self.name}'")
    
    def run(self, stop_on_failure: bool = True) -> Dict[str, Any]:
        """Run all tasks in the workflow"""
        self.last_run = datetime.datetime.now()
        logger.info(f"Running workflow '{self.name}'")
        
        results = {}
        for task in self.tasks:
            try:
                results[task.name] = task.run()
            except Exception as e:
                results[task.name] = {"error": str(e)}
                logger.error(f"Task '{task.name}' in workflow '{self.name}' failed: {str(e)}")
                if stop_on_failure:
                    logger.info(f"Stopping workflow '{self.name}' due to task failure")
                    break
        
        return results
    
    def save(self, filepath: Union[str, Path]) -> None:
        """Save workflow configuration to file"""
        data = {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "tasks": [task.name for task in self.tasks]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Workflow '{self.name}' configuration saved to {filepath}")

class AutomationManager:
    """Manages all automation workflows and tasks"""
    
    def __init__(self):
        self.workflows: Dict[str, AutomationWorkflow] = {}
        self.tasks: Dict[str, AutomationTask] = {}
        logger.info("Automation manager initialized")
    
    def register_task(self, task: AutomationTask) -> None:
        """Register a task with the manager"""
        self.tasks[task.name] = task
        logger.info(f"Task '{task.name}' registered")
    
    def register_workflow(self, workflow: AutomationWorkflow) -> None:
        """Register a workflow with the manager"""
        self.workflows[workflow.name] = workflow
        logger.info(f"Workflow '{workflow.name}' registered")
    
    def run_task(self, task_name: str, *args, **kwargs) -> Any:
        """Run a specific task by name"""
        if task_name not in self.tasks:
            raise ValueError(f"Task '{task_name}' not found")
        
        return self.tasks[task_name].run(*args, **kwargs)
    
    def run_workflow(self, workflow_name: str, stop_on_failure: bool = True) -> Dict[str, Any]:
        """Run a specific workflow by name"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        return self.workflows[workflow_name].run(stop_on_failure=stop_on_failure)
    
    def save_state(self, directory: Union[str, Path]) -> None:
        """Save the current state of all workflows and tasks"""
        directory = Path(directory)
        directory.mkdir(exist_ok=True, parents=True)
        
        # Save workflows
        workflows_dir = directory / "workflows"
        workflows_dir.mkdir(exist_ok=True)
        for name, workflow in self.workflows.items():
            workflow.save(workflows_dir / f"{name}.json")
        
        # Save tasks
        tasks_data = {name: task.to_dict() for name, task in self.tasks.items()}
        with open(directory / "tasks.json", 'w') as f:
            json.dump(tasks_data, f, indent=2)
        
        logger.info(f"Automation manager state saved to {directory}")

# Create a global instance of the automation manager
manager = AutomationManager()