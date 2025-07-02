module.exports.onRpcRequest = async ({ origin, request }) => {
  switch (request.method) {
    case 'hello':
      return 'Hello from Synergy Snap!';
    default:
      throw new Error('Method not found.');
  }
};
