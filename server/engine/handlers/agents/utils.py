from models import basic_model

def get_model(name):
    model_switcher = {
        'qnet': basic_model.QNet()
    }

    return model_switcher.get(name)
