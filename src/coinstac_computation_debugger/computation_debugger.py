import os
import json

class CoinstacComputationDebugger:
    def __init__(self, num_clients, path_to_test_input_dir="../test", debug_dir="../test/debug"):
        print("Initializing COINSTAC computation debugger..")
        self.num_clients = num_clients
        self.path_to_test_input_dir = path_to_test_input_dir
        self.__temp_dir_prefix = "temp_"

        self.debug_dir = debug_dir
        os.makedirs(self.debug_dir, exist_ok=True)

        # Create local and remote debug dirs if doesnot exist
        self.__local_transfer_dir=[None]*num_clients
        self.__local_out_dir=[None]*num_clients
        self.__local_cache_dir=[None]*num_clients

        for client_id in range(self.num_clients):
            self.__local_transfer_dir[client_id] = os.path.join(self.debug_dir, f'{self.__temp_dir_prefix}_rem_input', f'local{str(client_id)}')
            self.__local_out_dir[client_id] = os.path.join(self.debug_dir, f'{self.__temp_dir_prefix}_local{str(client_id)}_out')
            self.__local_cache_dir[client_id] = os.path.join(self.debug_dir, f'{self.__temp_dir_prefix}_local{str(client_id)}_cache')

            os.makedirs(self.__local_transfer_dir[client_id], exist_ok=True)
            os.makedirs(self.__local_out_dir[client_id], exist_ok=True)
            os.makedirs(self.__local_cache_dir[client_id], exist_ok=True)

        self.__rem_transfer_dir = os.path.join(self.debug_dir, f'{self.__temp_dir_prefix}_rem_trans')
        self.__rem_input_dir = os.path.join(self.debug_dir, f'{self.__temp_dir_prefix}_rem_input')
        self.__rem_output_dir = os.path.join(self.debug_dir, f'{self.__temp_dir_prefix}_rem_out')
        self.__rem_cache_dir = os.path.join(self.debug_dir, f'{self.__temp_dir_prefix}_rem_cache')

        os.makedirs(self.__rem_transfer_dir, exist_ok=True)
        os.makedirs(self.__rem_input_dir, exist_ok=True)
        os.makedirs(self.__rem_output_dir, exist_ok=True)

    def filter_sim_input_dict_keys(self, input_dict):
        new_input_dict = {}
        for key, key_val in input_dict.items():
            if 'value' in key_val:
                new_input_dict[key] = key_val['value']
            else:
                new_input_dict[key] = key_val
        return new_input_dict

    def get_local_args(self, input_dict, cache_dict, iteration_num, client_id, first_run=False):
        orig_input_dict = input_dict if type(input_dict) is dict else json.loads(input_dict)
        input_dict = self.filter_sim_input_dict_keys(orig_input_dict)

        return {'input': input_dict.get("output", input_dict),
                'cache': cache_dict,
                'state': {
                    'baseDirectory': os.path.join(self.path_to_test_input_dir, 'input', f'local{client_id}', 'simulatorRun')
                                        if first_run else self.__rem_transfer_dir,
                    'outputDirectory': self.__local_out_dir[client_id],
                    'cacheDirectory': self.__local_out_dir[client_id],
                    'transferDirectory': self.__local_transfer_dir[client_id],
                    'clientId': f'local{client_id}',
                    'iteration': iteration_num}}

    def get_remote_args(self, input_dict, cache_dict, iteration_num):
        input_dict = input_dict if type(input_dict) is dict else json.loads(input_dict)
        temp_dict = {}

        for client_id in range(self.num_clients):
            client_name = f'local{client_id}'
            client_dict = input_dict[client_name] if type(input_dict[client_name]) is dict else json.loads(
                input_dict[client_name])
            temp_dict[client_name] = client_dict["output"]

        return {'input': temp_dict,
                'cache': cache_dict,
                'state': {'baseDirectory': self.__rem_input_dir,
                          'outputDirectory': self.__rem_output_dir,
                          'cacheDirectory': self.__rem_output_dir,
                          'transferDirectory': self.__rem_transfer_dir,
                          'clientId': 'remote',
                          'iteration': iteration_num}}

    def run_iterations(self, inputspec_file_path, num_iterations, local_calls_list, remote_calls_list):
        __local_calls = list(local_calls_list)
        __remote_calls = list(remote_calls_list)
        inputspec = json.loads(open(inputspec_file_path).read())

        prev_rem_cache_dict = {}
        prev_rem_output = None
        prev_local_outputs_dict = None
        for curr_iter in range(1, num_iterations+1):
            curr_local_output_dicts={}
            curr_local_call = __local_calls.pop(0)
            for client_id in range(self.num_clients):
                if curr_iter ==1 :
                    new_args = self.get_local_args(inputspec[client_id], {}, curr_iter, client_id, first_run=True)
                else:
                    temp_prev_local_output_dict=prev_local_outputs_dict[f'local{client_id}']
                    prev_local_cache_dict=temp_prev_local_output_dict['cache'] if type(temp_prev_local_output_dict) is dict \
                                                else json.loads(temp_prev_local_output_dict)['cache']

                    new_args = self.get_local_args(prev_rem_output,
                                                   prev_local_cache_dict,
                                                   curr_iter, client_id, first_run=False)
                    prev_rem_cache_dict= prev_rem_output['cache'] if type(prev_rem_output) is dict \
                                            else json.loads(prev_rem_output)['cache']

                curr_local_output_dicts[f'local{client_id}'] = curr_local_call(new_args)

            curr_rem_call = __remote_calls.pop(0)
            curr_rem_output = curr_rem_call(self.get_remote_args(curr_local_output_dicts, prev_rem_cache_dict, curr_iter))

            prev_local_outputs_dict = curr_local_output_dicts
            prev_rem_output = curr_rem_output
        return prev_local_outputs_dict, prev_rem_output