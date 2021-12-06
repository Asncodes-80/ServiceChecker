import subprocess


class PowerShellCmd:
    ps_default_path = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"

    def run(self, cmd) -> str:
        result = str(
            subprocess.check_output([self.ps_default_path, cmd]).decode("utf-8")
        )
        return result

    def get_ping(self, node_ip_add: str):
        """Using the ps of windows in order to having more script flexibility..

        ping -n 1 will use for getting only one replay from ping command.
        Pipe "|" of select-string -pattern only for getting replay of ping.
        """
        try:
            res = self.run(f"ping -n 1 {node_ip_add} | select-string -pattern 'TTL='")
            # Will return 128 as ttl and keep that as string, to
            # getting only number of ttl like 64 or 128
            ttl = int(res.split(" ")[5].strip()[4:])  # make it integer
            # Check if ttl is not 0ms or above of 10ms, True is okay, and
            # False is not connected.
            return ttl > 10

        except Exception as err:
            print(f"Error in ping function: {err}")
            return 0
