B
    �|a  �               @   s�   d dl mZ d dlmZmZ G dd� de�ZG dd� de�ZG dd� de�ZG d	d
� d
e�ZG dd� de�Z	G dd� de�Z
dS )�    )�Optional)�	BaseModel�EmailStrc               @   s   e Zd ZU eed< eed< dS )�AssistantManagerBase�assistant_id�
manager_idN)�__name__�
__module__�__qualname__�int�__annotations__� r   r   �"./app/schemas/assistant_manager.pyr      s   
r   c               @   s   e Zd ZdS )�AssistantManagerCreateN)r   r	   r
   r   r   r   r   r      s   r   c               @   s.   e Zd ZU dZee ed< dZee ed< dS )�AssistantManagerUpdateNr   r   )r   r	   r
   r   r   r   r   r   r   r   r   r   r      s   
r   c               @   s,   e Zd ZU dZee ed< G dd� d�ZdS )�AssistantManagerInDBBaseN�idc               @   s   e Zd ZdZdS )zAssistantManagerInDBBase.ConfigTN)r   r	   r
   �orm_moder   r   r   r   �Config   s   r   )r   r	   r
   r   r   r   r   r   r   r   r   r   r      s   
r   c               @   s   e Zd ZdS )�AssistantManagerN)r   r	   r
   r   r   r   r   r      s   r   c               @   s   e Zd ZdS )�AssistantManagerInDBN)r   r	   r
   r   r   r   r   r   $   s   r   N)�typingr   �pydanticr   r   r   r   r   r   r   r   r   r   r   r   �<module>   s   