from lxml import etree
from jnpr.junos import jxml


class RpcError(Exception):
    """
    Parent class for all junos-pyez RPC Exceptions
    """
    def __init__(self, cmd=None, rsp=None, errs=None, dev=None, timeout=None):
        """
          :cmd: is the rpc command
          :rsp: is the rpc response (after <rpc-reply>)
          :errs: is a list of <rpc-error> elements
          :dev: is the device rpc was executed on
          :timeout: is the timeout value of the device
        """
        self.cmd = cmd
        self.rsp = rsp
        self.errs = errs
        self.dev = dev
        self.timeout = timeout

    def __repr__(self):
        """
          pprints the response XML attribute
        """
        if self.rsp is not None:
            self.rpc_error = jxml.rpc_error(self.rsp)
            if self.errs is None:
                self.errs = self.rpc_error
            return "{0}(severity: {1}, bad_element: {2}, message: {3})"\
                .format(self.__class__.__name__, self.rpc_error['severity'],
                        self.rpc_error['bad_element'], self.rpc_error['message'])

    __str__ = __repr__


class CommitError(RpcError):
    """
    Generated in response to a commit-check or a commit action.
    """
    def __init__(self, cmd=None, rsp=None, errs=None):
        RpcError.__init__(self, cmd, rsp, errs)
        self.rpc_error = jxml.rpc_error(rsp)
        if self.errs is None:
            self.errs = self.rpc_error

    def __repr__(self):
        return "{0}(edit_path: {1}, bad_element: {2}, message: {3})"\
            .format(self.__class__.__name__, self.rpc_error['edit_path'],
                    self.rpc_error['bad_element'], self.rpc_error['message'])

    __str__ = __repr__


class ConfigLoadError(RpcError):
    """
    Generated in response to a failure when loading a configuration.
    """
    def __init__(self, cmd=None, rsp=None, errs=None):
        RpcError.__init__(self, cmd, rsp, errs)
        self.rpc_error = jxml.rpc_error(rsp)
        if self.errs is None:
            self.errs = self.rpc_error

    def __repr__(self):
        return "{0}(severity: {1}, bad_element: {2}, message: {3})"\
            .format(self.__class__.__name__, self.rpc_error['severity'],
                    self.rpc_error['bad_element'], self.rpc_error['message'])

    __str__ = __repr__


class LockError(RpcError):
    """
    Generated in response to attempting to take an exclusive
    lock on the configuration database.
    """
    def __init__(self, rsp):
        RpcError.__init__(self, rsp=rsp)
        self.rpc_error = jxml.rpc_error(rsp)


class UnlockError(RpcError):
    """
    Generated in response to attempting to unlock the
    configuration database.
    """
    def __init__(self, rsp):
        RpcError.__init__(self, rsp=rsp)
        self.rpc_error = jxml.rpc_error(rsp)


class PermissionError(RpcError):
    """
    Generated in response to invoking an RPC for which the
    auth user does not have user-class permissions.

    PermissionError.message gives you the specific RPC that cause
    the exceptions
    """
    def __init__(self, cmd=None, rsp=None):
        RpcError.__init__(self, cmd=cmd, rsp=rsp)
        self.message = rsp.findtext('.//bad-element')


class RpcTimeoutError(RpcError):
    """
    Generated in response to a RPC execution timeout.
    """
    def __init__(self, dev, cmd, timeout):
        RpcError.__init__(self, dev=dev, cmd=cmd, timeout=timeout)

    def __repr__(self):
        return "{0}(host: {1}, cmd: {2}, timeout: {3})"\
            .format(self.__class__.__name__, self.dev.hostname, self.cmd, self.timeout)

    __str__ = __repr__


# ================================================================
# ================================================================
#                    Connection Exceptions
# ================================================================
# ================================================================


class ConnectError(Exception):
    """
    Parent class for all connection related exceptions
    """

    @property
    def user(self):
        """ login user-name """
        return self.dev.user

    @property
    def host(self):
        """ login host name/ipaddr """
        return self.dev.hostname

    @property
    def port(self):
        """ login SSH port """
        return self.dev._port

    def __init__(self, dev):
        self.dev = dev
        # @@@ need to attach attributes for each access
        # @@@ to user-name, host, jump-host, etc.

    def __repr__(self):
        return "{0}({1})".format(
            self.__class__.__name__,
            self.dev.hostname)

    __str__ = __repr__


class ProbeError(ConnectError):
    """
    Generated if auto_probe is enabled and the probe action fails
    """
    pass


class ConnectAuthError(ConnectError):
    """
    Generated if the user-name, password is invalid
    """
    pass


class ConnectTimeoutError(ConnectError):
    """
    Generated if the NETCONF session fails to connect, could
    be due to the fact the device is not ip reachable; bad
    ipaddr or just due to routing
    """
    pass


class ConnectUnknownHostError(ConnectError):
    """
    Generated if the specific hostname does not DNS resolve
    """
    pass


class ConnectRefusedError(ConnectError):
    """
    Generated if the specified host denies the NETCONF; could
    be that the services is not enabled, or the host has
    too many connections already.
    """
    pass


class ConnectNotMasterError(ConnectError):
    """
    Generated if the connection is made to a non-master
    routing-engine.  This could be a backup RE on an MX
    device, or a virtual-chassis member (linecard), for example
    """
    pass
